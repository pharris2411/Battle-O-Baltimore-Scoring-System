from django.forms import ModelForm
from models import *

class MatchForm(ModelForm):
	class Meta:
		model = Match

# class ProjectForm(ModelForm):
# 	class Meta:
# 		model = Project

# class RoomForm(ModelForm):
# 	class Meta:
# 		model = Room
# 		exclude = ('project')

# class RequirementForm(ModelForm):
# 	class Meta:
# 		model = Requirement
# 		exclude = ('project')

# class SelectedItemForm(ModelForm):
# 	class Meta:
# 		model = SelectedItem
# 		exclude = ('project')

# class CollectionForm(ModelForm):
# 	class Meta:
# 		model = Collection
# 		exclude = ('project')

# class TaskForm(ModelForm):
# 	class Meta:
# 		model = Task
# 		exclude = ('project')