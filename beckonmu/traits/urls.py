"""
URL configuration for traits API endpoints.
"""

from django.urls import path
from .api import (
    TraitCategoriesAPI,
    TraitsAPI,
    DisciplinePowersAPI,
    CharacterValidationAPI,
    CharacterImportAPI,
    CharacterExportAPI,
    CharacterAvailableTraitsAPI
)

app_name = 'traits'

urlpatterns = [
    # Trait data endpoints
    path('api/traits/categories/', TraitCategoriesAPI.as_view(), name='categories'),
    path('api/traits/', TraitsAPI.as_view(), name='list'),
    path('api/traits/discipline-powers/', DisciplinePowersAPI.as_view(), name='discipline_powers'),
    
    # Character management endpoints
    path('api/traits/character/validate/', CharacterValidationAPI.as_view(), name='character_validate'),
    path('api/traits/character/import/', CharacterImportAPI.as_view(), name='character_import'),
    path('api/traits/character/<int:character_id>/export/', CharacterExportAPI.as_view(), name='character_export'),
    path('api/traits/character/<int:character_id>/available-traits/', CharacterAvailableTraitsAPI.as_view(), name='character_available_traits'),
]
