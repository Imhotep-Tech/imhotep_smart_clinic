# 🛡️ Admin Portal & Multi-Tenant Query Scoping

This document explains the Django Admin integration, permissions model, and query scoping implementation in `accounts/admin.py`.

---

## 🔒 Multi-Tenant Data Isolation

In Imhotep Smart Clinic, **Clinic Admin** users (`user_type='clinic_admin'`) must only see and edit data belonging to their specific clinic. They must **never** see or modify records from other clinics or superuser accounts.

To enforce this security boundary, all Django ModelAdmin classes inherit from `ScopedModelAdmin`.

---

## 🛠️ `ScopedModelAdmin` Implementation

`ScopedModelAdmin` in `accounts/admin.py` overrides `get_queryset()` and explicit permission handlers:

```python
def get_user_clinic(user):
    if not user or not user.is_authenticated:
        return None
    if user.is_clinic_admin():
        return Clinic.objects.filter(admin=user).first()
    return None

class ScopedModelAdmin(admin.ModelAdmin):
    """
    Base ModelAdmin that scopes queries for Clinic Admin users so they can only access their clinic's data.
    """
    def has_module_permission(self, request):
        if request.user.is_superuser or getattr(request.user, 'is_super_admin', lambda: False)():
            return True
        if getattr(request.user, 'is_clinic_admin', lambda: False)():
            return True
        return super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser or getattr(request.user, 'is_super_admin', lambda: False)():
            return True
        if getattr(request.user, 'is_clinic_admin', lambda: False)():
            return True
        return super().has_view_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or getattr(request.user, 'is_super_admin', lambda: False)():
            return True
        if getattr(request.user, 'is_clinic_admin', lambda: False)():
            return True
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request):
        if request.user.is_superuser or getattr(request.user, 'is_super_admin', lambda: False)():
            return True
        if getattr(request.user, 'is_clinic_admin', lambda: False)():
            return True
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser or getattr(request.user, 'is_super_admin', lambda: False)():
            return True
        if getattr(request.user, 'is_clinic_admin', lambda: False)():
            return True
        return super().has_delete_permission(request, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.is_super_admin():
            return qs
        if request.user.is_clinic_admin():
            clinic = get_user_clinic(request.user)
            if not clinic:
                return qs.none()
            if self.model == Clinic:
                return qs.filter(id=clinic.id)
            elif self.model == DoctorProfile:
                return qs.filter(clinic=clinic)
            elif self.model == Patients:
                return qs.filter(clinic=clinic)
            elif self.model == AssistantProfile:
                return qs.filter(clinic=clinic)
            elif self.model == MedicalRecord:
                return qs.filter(clinic=clinic)
            elif self.model == Appointments:
                return qs.filter(clinic=clinic)
            elif self.model == AppointmentTimes:
                return qs.filter(doctor__clinic=clinic)
        return qs
```

---

## 📋 Scoped Model Summary

Every model registered in `accounts/admin.py` is protected by `ScopedModelAdmin`:

| Registered Model | Scoped Behavior for Clinic Admins |
| :--- | :--- |
| **`Clinic`** | Displays **only** the admin's own Clinic. |
| **`DoctorProfile`** | Displays **only** doctors assigned to the admin's Clinic. |
| **`Patients`** | Displays **only** patients belonging to the admin's Clinic. |
| **`AssistantProfile`** | Displays **only** assistants attached to the admin's Clinic. |
| **`MedicalRecord`** | Displays **only** medical records under the admin's Clinic. |
| **`Appointments`** | Displays **only** appointments scheduled at the admin's Clinic. |
| **`AppointmentTimes`** | Displays **only** slot schedules for doctors in the admin's Clinic. |
| **`User` (`CustomUserAdmin`)** | Displays **only** user accounts (doctors, assistants, patients) linked to the admin's Clinic + the admin themselves. |

---

## 🔑 Key Inlines & Fixes

- **`PatientsInline`**: Set `fk_name = 'doctor'` explicitly to fix Django inline validation error `E202`.
- **`PatientsAdmin`**: Configured `list_filter` and `search_fields` to look up paths (`doctor__user__username`, `clinic__name`).
