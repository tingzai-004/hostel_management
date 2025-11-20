from django import forms

class  BootStrapModelForm(forms.ModelForm):
    bootstrap_exclude=[]
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for name,field in self .fields.items():
            if name in self.bootstrap_exclude:
                continue
            if field .widget.attrs:
                field.widget.attrs["class"]="form-control"
                field.widget.attrs["placeholder"]=field.label
            else:
                field.widget.attrs={
                    "class":"form-control",
                    "placeholder":field.label
                }
class BootStrapForm(forms.Form):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for name,field in self .fields.items():
            if field .widget.attrs:
                field.widget.attrs["class"]="form-control"
                field.widget.attrs["placeholder"]=field.label
            else:
                field.widget.attrs={
                    "class":"form-control",
                    "placeholder":field.label
                }