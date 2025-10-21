"""
Web API endpoints for enhanced character creation and trait management.
Provides JSON-based endpoints for web-based character applications.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.db import models
from evennia.objects.models import ObjectDB
from evennia.accounts.models import AccountDB
import json

from .utils import (
    enhanced_import_character_from_json,
    export_character_to_json,
    get_available_traits_for_character,
    validate_trait_for_character
)
from .models import TraitCategory, Trait, DisciplinePower


class BaseAPIView(View):
    """Base class for API views with common functionality."""

    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to handle JSON parsing."""
        if request.content_type == 'application/json' and hasattr(request, 'body'):
            try:
                request.json = json.loads(request.body.decode('utf-8'))
            except (ValueError, UnicodeDecodeError):
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
        else:
            request.json = {}

        return super().dispatch(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class TraitCategoriesAPI(BaseAPIView):
    """API endpoint for trait categories."""

    def get(self, request):
        """Get all trait categories."""
        categories = TraitCategory.objects.all()
        data = []

        for category in categories:
            data.append({
                'id': category.id,
                'name': category.name,
                'code': category.code,
                'description': category.description,
                'sort_order': category.sort_order
            })

        return JsonResponse({'categories': data})


@method_decorator(csrf_exempt, name='dispatch')
class TraitsAPI(BaseAPIView):
    """API endpoint for traits."""

    def get(self, request):
        """Get traits, optionally filtered by category or splat."""
        category_code = request.GET.get('category')
        splat = request.GET.get('splat', 'mortal')

        traits = Trait.objects.filter(is_active=True)

        if category_code:
            traits = traits.filter(category__code=category_code)

        # Filter by splat restriction
        if splat:
            traits = traits.filter(
                models.Q(splat_restriction__isnull=True) |
                models.Q(splat_restriction='') |
                models.Q(splat_restriction=splat)
            )

        traits = traits.select_related('category').order_by('category__sort_order', 'sort_order', 'name')

        data = []
        for trait in traits:
            data.append({
                'id': trait.id,
                'name': trait.name,
                'category': trait.category.code,
                'category_name': trait.category.name,
                'description': trait.description,
                'min_value': trait.min_value,
                'max_value': trait.max_value,
                'is_instanced': trait.is_instanced,
                'has_specialties': trait.has_specialties,
                'splat_restriction': trait.splat_restriction
            })

        return JsonResponse({'traits': data})


@method_decorator(csrf_exempt, name='dispatch')
class DisciplinePowersAPI(BaseAPIView):
    """API endpoint for discipline powers."""

    def get(self, request):
        """Get discipline powers, optionally filtered by discipline."""
        discipline_name = request.GET.get('discipline')
        level = request.GET.get('level')

        powers = DisciplinePower.objects.filter(is_active=True)

        if discipline_name:
            powers = powers.filter(discipline__name__iexact=discipline_name)

        if level:
            try:
                powers = powers.filter(level=int(level))
            except ValueError:
                return JsonResponse({'error': 'Invalid level parameter'}, status=400)

        powers = powers.select_related('discipline', 'amalgam_discipline').order_by(
            'discipline__name', 'level', 'sort_order', 'name'
        )

        data = []
        for power in powers:
            data.append({
                'id': power.id,
                'name': power.name,
                'discipline': power.discipline.name,
                'level': power.level,
                'description': power.description,
                'dice_pool': power.dice_pool,
                'cost': power.cost,
                'duration': power.duration,
                'amalgam_discipline': power.amalgam_discipline.name if power.amalgam_discipline else None,
                'amalgam_level': power.amalgam_level,
                'requirements_text': power.requirements_text
            })

        return JsonResponse({'powers': data})


@method_decorator(csrf_exempt, name='dispatch')
class CharacterValidationAPI(BaseAPIView):
    """API endpoint for character validation."""

    def post(self, request):
        """Validate character data without creating the character."""
        character_data = request.json

        if not character_data:
            return JsonResponse({'error': 'No character data provided'}, status=400)

        # Create a temporary character object for validation
        temp_char = ObjectDB()
        temp_char.db_key = character_data.get('name', 'TempChar')

        # Run validation
        results = enhanced_import_character_from_json(temp_char, character_data, validate_only=True)

        return JsonResponse({
            'valid': results['success'],
            'errors': results['validation_errors'] + results['errors'],
            'warnings': results['warnings'],
            'summary': {
                'traits_validated': results['imported_traits'],
                'specialties_validated': results['imported_specialties'],
                'powers_validated': results['imported_powers']
            }
        })


@method_decorator(csrf_exempt, name='dispatch')
class CharacterImportAPI(BaseAPIView):
    """API endpoint for character import."""

    def post(self, request):
        """Import character data to an existing character."""
        character_name = request.json.get('character_name')
        character_data = request.json.get('character_data')
        account_name = request.json.get('account_name')

        if not all([character_name, character_data, account_name]):
            return JsonResponse({
                'error': 'Missing required fields: character_name, character_data, account_name'
            }, status=400)

        try:
            # Get the account
            account = AccountDB.objects.get(username__iexact=account_name)

            # Get the character
            character = ObjectDB.objects.get(
                db_key__iexact=character_name,
                db_account=account,
                db_typeclass_path__contains='characters'
            )

        except AccountDB.DoesNotExist:
            return JsonResponse({'error': f'Account {account_name} not found'}, status=404)
        except ObjectDB.DoesNotExist:
            return JsonResponse({'error': f'Character {character_name} not found for account {account_name}'}, status=404)

        # Import the character data
        results = enhanced_import_character_from_json(character, character_data)

        return JsonResponse({
            'success': results['success'],
            'errors': results['errors'],
            'warnings': results['warnings'],
            'imported': {
                'traits': results['imported_traits'],
                'specialties': results['imported_specialties'],
                'powers': results['imported_powers']
            },
            'validation_errors': results['validation_errors']
        })


@method_decorator(csrf_exempt, name='dispatch')
class CharacterExportAPI(BaseAPIView):
    """API endpoint for character export."""

    def get(self, request, character_id):
        """Export character data to JSON format."""
        try:
            character = ObjectDB.objects.get(id=character_id, db_typeclass_path__contains='characters')
        except ObjectDB.DoesNotExist:
            return JsonResponse({'error': 'Character not found'}, status=404)

        include_powers = request.GET.get('include_powers', 'true').lower() == 'true'

        character_data = export_character_to_json(character, include_powers=include_powers)

        return JsonResponse({
            'character_data': character_data,
            'character_name': character.key,
            'exported_at': character_data.get('updated_at', 'unknown')
        })


@method_decorator(csrf_exempt, name='dispatch')
class CharacterAvailableTraitsAPI(BaseAPIView):
    """API endpoint for getting available traits for a character."""

    def get(self, request, character_id):
        """Get all traits available to a specific character based on their splat."""
        try:
            character = ObjectDB.objects.get(id=character_id, db_typeclass_path__contains='characters')
        except ObjectDB.DoesNotExist:
            return JsonResponse({'error': 'Character not found'}, status=404)

        available_traits = get_available_traits_for_character(character)

        data = []
        for trait in available_traits:
            data.append({
                'id': trait.id,
                'name': trait.name,
                'category': trait.category.code,
                'category_name': trait.category.name,
                'description': trait.description,
                'min_value': trait.min_value,
                'max_value': trait.max_value,
                'is_instanced': trait.is_instanced,
                'has_specialties': trait.has_specialties,
                'splat_restriction': trait.splat_restriction
            })

        return JsonResponse({'available_traits': data})


# URL patterns for inclusion in main urls.py
def get_api_urls():
    """Return URL patterns for the trait API."""
    from django.urls import path

    return [
        path('api/traits/categories/', TraitCategoriesAPI.as_view(), name='trait_categories_api'),
        path('api/traits/', TraitsAPI.as_view(), name='traits_api'),
        path('api/discipline-powers/', DisciplinePowersAPI.as_view(), name='discipline_powers_api'),
        path('api/character/validate/', CharacterValidationAPI.as_view(), name='character_validation_api'),
        path('api/character/import/', CharacterImportAPI.as_view(), name='character_import_api'),
        path('api/character/<int:character_id>/export/', CharacterExportAPI.as_view(), name='character_export_api'),
        path('api/character/<int:character_id>/available-traits/', CharacterAvailableTraitsAPI.as_view(), name='character_available_traits_api'),
    ]
