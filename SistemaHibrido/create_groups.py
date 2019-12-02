from django.contrib.auth.models import Group
from django.contrib.auth.models import User
group = Group(name="admin")
group.save()
group = Group(name="coordenador")
group.save()
staff = User.objects.filter(is_staff=True)
staff = User.objects.get(username=staff[0])
group = Group.objects.get(name='admin')
staff.groups.add(group)
group = Group.objects.get(name='coordenador')
staff.groups.add(group)