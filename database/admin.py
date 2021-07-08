import os
import csv

from itertools import chain

from django.contrib import admin, messages
from django.http import HttpResponse

from .forms import SessionForm
from .models import Student, Project, Session, Year, GradeYearAssociation
from django.conf import settings



# Register your models here.


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    actions = ['export_project_summary']

    def export_project_summary(modeladmin, request, queryset):
        if queryset.count() != 1:
            messages.error(request, 'Please select only one project')
        else:
            project = queryset.last()
            response = HttpResponse(
                content_type='text/csv',
                headers={'Content-Disposition':
                    f'attachment; filename="Summary_{project.title}.csv'}
            )
            spamwriter = csv.writer(response)

            # Project informations
            spamwriter.writerow(['Project'])
            spamwriter.writerow([project.title])
            spamwriter.writerow([])

            # Initialize variables
            years = list(Year.objects.all())
            sum_list = [project.compute_sum(year) for year in years]
            while not sum_list[0]:
                sum_list.pop(0)
                years.pop(0)
            while not sum_list[-1]:
                sum_list.pop(-1)
                years.pop(-1)
            table = [['']*len(years)*2
                for i in range(max(len(l) for l in sum_list) + 3)]

            # Add year
            for i in range(len(years)):
                table[0][2*i] = years[i].name

            # Add students by column
            for i in range(len(sum_list)):
                j = 1
                total = 0
                for (student, time) in sum_list[i].items():
                    table[j][2*i] = str(student)
                    table[j][2*i + 1] = str(time)
                    j += 1
                    total += time
                table[j][2*i] = 'TOTAL'
                table[j][2*i + 1] = str(total)

            for line in table:
                spamwriter.writerow(line)
            return response


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    form = SessionForm
    filter_horizontal = ('students', )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    actions = ['export_student_summary_schooling']
    search_fields = [
        'first_name',
        'last_name',
    ]

    def export_student_summary_schooling(modeladmin, request, queryset):
        if queryset.count() != 1:
            messages.error(request, 'Please select only one student')
        else:
            student = queryset.last()
            response = HttpResponse(
                content_type='text/csv',
                headers={'Content-Disposition': 
                    f'attachment; filename="Summary_{student.first_name}_' +
                    f'{student.last_name}_schooling.csv"'}
            )
            spamwriter = csv.writer(response)

            # Student informations
            spamwriter.writerow(['First name', 'Last name'])
            spamwriter.writerow([
                student.first_name,
                student.last_name,
            ])
            spamwriter.writerow([])

            # Initialize variables
            gya_list = GradeYearAssociation.objects.filter(
                    student=student
                ).order_by('year').select_related('year')
            years = [gya.year for gya in gya_list]
            sum_list = [student.compute_sum(year) for year in years]
            table = [['']*len(years)*2
                for i in range(max(len(l) for l in sum_list) + 4)]

            # Add years and grade
            for i in range(len(years)):
                table[0][2*i] = years[i].name
                table[1][2*i] = f'Grade {gya_list[i].grade}'

            # Add projects by columns
            for i in range(len(sum_list)):
                j = 2
                total = 0
                for (project, time) in sum_list[i].items():
                    table[j][2*i] = project
                    table[j][2*i + 1] = str(time)
                    j += 1
                    total += time
                table[j][2*i] = 'TOTAL'
                table[j][2*i + 1] = str(total)

            for line in table:
                spamwriter.writerow(line)
            return response


@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
    actions = ['import_update_students']

    def import_update_students(modeladmin, request, queryset):
        # Le queryset ne doit contenir qu’une seule date
        if queryset.count() != 1:
            messages.error(request, 'Please select only one year')
        else:
            year = queryset.first()
            # Normalement, il y aura un appel à l’API, renvoyant la
            # liste des élèves. On va donc simuler cette fonction.
            students_dicts = Student.get_from_api(year, request)
            new_students_list = []
            students_objects = []
            for data in students_dicts:
                try:
                    student = Student.objects.get(database_id = data['id'])
                except Student.DoesNotExist:
                    student = Student(
                        first_name = data['first_name'],
                        last_name = data['last_name'],
                        database_id = data['id']
                    )
                    new_students_list.append(student)
                students_objects.append(student)

            Student.objects.bulk_create(new_students_list)

            gya_objects = []

            for i in range(len(students_dicts)):
                gya_objects.append(GradeYearAssociation(
                    year = year,
                    grade = students_dicts[i]['grade'],
                    student = students_objects[i]
                ))
            
            GradeYearAssociation.objects.bulk_create(gya_objects)


@admin.register(GradeYearAssociation)
class GradeYearAdmin(admin.ModelAdmin):
    pass
