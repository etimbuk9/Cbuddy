from django.forms import *

class NewDrugForm(Form):
    name = CharField(widget=TextInput(attrs={
        'class':'form-control'
    }))
    category = ChoiceField(
        widget=Select(attrs={'class':'form-control'}),
        choices=[(x,x) for x in sorted(['Tablets', 'Syrups', 'Injectables', 'Consumables','Fluids','Suspensions', 'Topicals', 'Capsules'])]
    )
    prescription_unit = ChoiceField(
        widget=Select(attrs={'class':'form-control'}),
        choices=[(x,x) for x in sorted(['*','CAPS','DROP','IVF','MILS','PUFFS','SP','TABS','TOPS','VIAL','MU','tt','Mcg'])]
    )
    store_unit = ChoiceField(
        widget=Select(attrs={'class':'form-control'}),
        choices=[(x,x) for x in sorted(['*','CAPS','DROP','IVF','MILS','PUFFS','SP','TABS','TOPS','VIAL','MU','tt','Mcg'])]
    )
    amount_per_unit = FloatField(
        widget=NumberInput(attrs={'class':'form-control'}), 
        initial=1.0,
    )
    directly_dispensable = ChoiceField(
        choices=(('Yes', 'Yes'), ('No', 'No')), 
        widget=Select(attrs={'class':'form-control'}),
    )
    quantity = FloatField(
        widget=NumberInput(attrs={'class':'form-control'}), 
        initial=1.0,
    )