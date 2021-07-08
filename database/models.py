from datetime import date, datetime
from requests import post

from django.conf import settings
from django.db import models

# Create your models here.
class Student(models.Model):
    database_id = models.IntegerField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_from_api(year, request):
        now_timestamp = datetime.timestamp(datetime.now())
        if (not 'access_token' in request.session.keys() or
            ('expires_at' in request.session.keys() and
            request.session['expires_at'] < now_timestamp)):
                token_request = post(
                    'http://api-sim.happychandara.org/oauth/token', headers={
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }, data={
                        'grant_type': 'client_credentials',
                        'client_id': settings.CLIENT_ID,
                        'client_secret': settings.CLIENT_SECRET,
                })
                deserialized = token_request.json()
                print(deserialized)
                request.session['access_token'] = deserialized['access_token']
                request.session['expires_at'] = (deserialized['expires_in']
                    + datetime.timestamp(datetime.now()))
                print('kouille')

        user_request = post('http://api-sim.happychandara.org/api/student/show',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {request.session["access_token"]}'
            })


        data = user_request.json()['data']
        userlist = []
        for user in data:
            if any(key not in user or not user[key] 
                for key in ['first_name', 'last_name', 'classname', 'id']):
                    continue
            print(user)
            if (user['classname'].startswith('H')
                            or user['classname'].startswith('14')):
                    grade = 14
            elif (user['classname'].startswith('B')
                            or user['classname'].startswith('13')):
                    grade = 13
            elif (grade_str := user['classname'][:2]) in ['10', '11', '12']:
                grade = int(grade_str)
            else:
                grade = int(user['classname'][0])

            userlist.append({
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'id': user['id'],
                'grade': grade
            })

        return userlist

    def compute_sum(self, year):
        sum_by_project = {}
        sessions = Session.objects.filter(students__pk=self.pk, year=year)
        for session in sessions:
            if session.project.title in sum_by_project.keys():
                sum_by_project[session.project.title] += session.duration
            else:
                sum_by_project[session.project.title] = session.duration
        return sum_by_project


class Project(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    def compute_sum(self, year):
        sum_by_student = {}
        sessions = Session.objects.filter(project=self, year=year)
        for session in sessions:
            for student in session.students.all():
                if student in sum_by_student.keys():
                    sum_by_student[student] += session.duration
                else:
                    sum_by_student[student] = session.duration
        return sum_by_student


class Year(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Session(models.Model):
    duration = models.FloatField()
    date = models.DateField(default=date.today)
    project = models.ForeignKey(to=Project, on_delete=models.SET_NULL,
        null=True)
    students = models.ManyToManyField(to=Student)
    year = models.ForeignKey(to=Year, on_delete=models.SET_NULL, blank=True,
        null=True)

    def __str__(self):
        return f'Session of the {self.date} for the project {self.project}'

    def save(self):
        if not self.year and not Year.objects.count() == 0:
            self.year = Year.objects.last()
        return super(Session, self).save()


class GradeYearAssociation(models.Model):

    class Meta:
        unique_together = ('year', 'student')

    year = models.ForeignKey(to=Year, on_delete=models.CASCADE)
    grade = models.IntegerField(choices=[(i, i) for i in range(1, 15)])
    student = models.ForeignKey(to=Student, on_delete=models.CASCADE)

    def __str__(self):
        return (f'In {self.year}, {self.student} was in grade {self.grade}')
