from django import forms
from django.contrib.auth.models import User
from assets.models import (
    Asset, Purchase, Transfer, Assignment, 
    Expenditure, Base, EquipmentType, Personnel
)


class PurchaseForm(forms.ModelForm):
    """Form for recording asset purchases"""
    
    class Meta:
        model = Purchase
        fields = ['asset', 'quantity', 'supplier', 'reference_number', 'cost', 'notes']
        widgets = {
            'asset': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'supplier': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Supplier name'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reference/Invoice number'
            }),
            'cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes'
            }),
        }


class TransferForm(forms.ModelForm):
    """Form for initiating asset transfers"""
    
    class Meta:
        model = Transfer
        fields = ['equipment_type', 'quantity', 'from_base', 'to_base', 'reference_number', 'notes']
        widgets = {
            'equipment_type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'from_base': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'to_base': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Transfer reference number'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        from_base = cleaned_data.get('from_base')
        to_base = cleaned_data.get('to_base')
        
        if from_base and to_base and from_base == to_base:
            raise forms.ValidationError("Cannot transfer to the same base.")
        
        return cleaned_data


class AssignmentForm(forms.ModelForm):
    """Form for assigning assets to personnel"""
    
    class Meta:
        model = Assignment
        fields = ['asset', 'personnel', 'quantity', 'notes']
        widgets = {
            'asset': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'personnel': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes'
            }),
        }


class ExpenditureForm(forms.ModelForm):
    """Form for recording asset expenditures"""
    
    class Meta:
        model = Expenditure
        fields = ['asset', 'quantity', 'reason', 'reference_number', 'notes']
        widgets = {
            'asset': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reason for expenditure'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reference number'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional details'
            }),
        }


class DashboardFilterForm(forms.Form):
    """Form for dashboard filtering"""
    
    base = forms.ModelChoiceField(
        queryset=Base.objects.all(),
        required=False,
        empty_label="All Bases",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    equipment_type = forms.ModelChoiceField(
        queryset=EquipmentType.objects.all(),
        required=False,
        empty_label="All Equipment Types",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


class ReturnAssignmentForm(forms.Form):
    """Form for returning assigned assets"""
    assignment = forms.ModelChoiceField(
        queryset=Assignment.objects.filter(return_date__isnull=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Return notes'
        })
    )
