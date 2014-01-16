from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from models import *
from django.contrib.auth.models import User
from django.db import IntegrityError
from tastypie.exceptions import BadRequest

class UserResource(ModelResource):
    class Meta:
        object_class = User
        queryset = User.objects.all()
        authorization = Authorization()
        include_resource_uri = False
        always_return_data = True
        resource_name = 'user'
        excludes = ['date_joined', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'password']
        filtering = {'username': ALL,}
        allowed_methods = ['get','patch','post']
    def obj_create(self, bundle, request=None, **kwargs):
        username, password = bundle.data['username'], bundle.data['password']
        try :
            bundle.obj = User.objects.create_user(username, '', password)
        except IntegrityError:
            raise BadRequest('That username already exists')
        return bundle

class RefResource(ModelResource):
    owner = fields.ForeignKey(UserResource, 'owner', full=True, help_text = "URI of the profile of the owner. When objects are uploaded from the R package, this field is set automatically.")
    def dehydrate(self, bundle):
        bundle.data['id'] = str(bundle.data['id'])
        bundle.data['owner'] = str(bundle.data['owner'].data['username'])
        return bundle
    class Meta:
        queryset = Ref.objects.all()
        authorization = Authorization()
        include_resource_uri = False
        always_return_data = True
        resource_name = 'reference'
        allowed_methods = ['get','post','patch']

class TraitResource(ModelResource):
    owner = fields.ForeignKey(UserResource, 'owner', full=True)
    def dehydrate(self, bundle):
        bundle.data['id'] = str(bundle.data['id'])
        bundle.data['owner'] = str(bundle.data['owner'].data['username'])
        return bundle
    class Meta:
        queryset = Trait.objects.all()
        authorization = Authorization()
        include_resource_uri = False
        always_return_data = True
        resource_name = 'trait'
        allowed_methods = ['get','post','patch']

class EnvironmentResource(ModelResource):
    owner = fields.ForeignKey(UserResource, 'owner', full=True)
    def dehydrate(self, bundle):
        bundle.data['id'] = str(bundle.data['id'])
        bundle.data['owner'] = str(bundle.data['owner'].data['username'])
        return bundle
    class Meta:
        queryset = Environment.objects.all()
        authorization = Authorization()
        include_resource_uri = False
        always_return_data = True
        resource_name = 'environment'
        allowed_methods = ['get','post','patch']

class TaxaResource(ModelResource):
    owner = fields.ForeignKey(UserResource, 'owner', full=True, help_text = "URI of the taxa owner. When submitting from the R package, this field is populated automatically.")
    def dehydrate(self, bundle):
        bundle.data['id'] = str(bundle.data['id'])
        bundle.data['owner'] = str(bundle.data['owner'].data['username'])
        return bundle
    class Meta:
        queryset = Taxa.objects.all()
        authorization = Authorization()
        include_resource_uri = False
        always_return_data = True
        resource_name = 'taxa'
        filtering = {
                'name': ALL,
                'vernacular': ALL,
                'gbif': ALL,
                'eol': ALL,
                'itis': ALL,
                'ncbi': ALL,
                'bold': ALL,
                'owner': ALL_WITH_RELATIONS,
                }
        allowed_methods = ['get','post','patch']

class PopulationResource(ModelResource):
    owner = fields.ForeignKey(UserResource, 'owner', full=True)
    taxa = fields.ForeignKey(TaxaResource, 'taxa', full=True, help_text = "The identifier (or URI) of the taxa object to which the population belongs.")
    def dehydrate(self, bundle):
        bundle.data['taxa'] = str(bundle.obj.taxa_id)
        bundle.data['id'] = str(bundle.data['id'])
        bundle.data['owner'] = str(bundle.data['owner'].data['username'])
        return bundle
    class Meta:
        authorization = Authorization()
        always_return_data = True
        queryset = Population.objects.all()
        include_resource_uri = False
        filtering = {
                'taxa': ALL_WITH_RELATIONS,
                'name': ALL,
                'description': ALL,
                'owner': ALL_WITH_RELATIONS,
                }
        resource_name = 'population'
        allowed_methods = ['get','post','patch']

class ItemResource(ModelResource):
    population = fields.ForeignKey(PopulationResource, 'population', full=True, help_text = "The identifier (or URI) of the population object to which the item belongs.")
    owner = fields.ForeignKey(UserResource, 'owner', full=True)
    traits = fields.ManyToManyField(TraitResource, 'traits', full=True, blank = True, null = True, help_text = "A list of traits values indentifiers (or URIs) that were measured on this item.")
    def dehydrate(self, bundle):
        bundle.data['population'] = str(bundle.obj.population_id)
        bundle.data['id'] = str(bundle.data['id'])
        bundle.data['owner'] = str(bundle.data['owner'].data['username'])
        bundle.data['traits'] = [str(tr.data['id']) for tr in bundle.data['traits']]
        return bundle
    def build_schema(self):
        base_schema = super(ItemResource, self).build_schema()
        for f in self._meta.object_class._meta.fields:
            if f.name in base_schema['fields'] and f.choices:
                base_schema['fields'][f.name].update({
                    'choices': [cho[0] for cho in f.choices],
                    })
        return base_schema
    class Meta:
        authorization = Authorization()
        always_return_data = True
        queryset = Item.objects.all()
        include_resource_uri = False
        filtering = {
                'population': ALL_WITH_RELATIONS,
                'description': ALL,
                'owner': ALL_WITH_RELATIONS,
                'stage': ALL,
                'level': ALL,
                }
        resource_name = 'item'
        allowed_methods = ['get','post','patch']

class InteractionResource(ModelResource):
    owner = fields.ForeignKey(UserResource, 'owner', full=True, help_text = "Who uploaded the data. URI of the data owner.")
    taxa_from = fields.ForeignKey(TaxaResource, 'taxa_from', full=True, help_text = "Identifier (or URI) of the taxa establishing the interaction.")
    taxa_to = fields.ForeignKey(TaxaResource, 'taxa_to', full=True, help_text = "Identifier (or URI) of the taxa receiving the interaction.")
    pop_from = fields.ForeignKey(PopulationResource, 'pop_from', full=True, null = True, help_text = "Identifier (or URI) of the pop. establishing the interaction.")
    pop_to = fields.ForeignKey(PopulationResource, 'pop_to', full=True, null = True, help_text = "Identifier (or URI) of the pop. receiving the interaction.")
    item_from = fields.ForeignKey(ItemResource, 'item_from', full=True, null = True, blank = True, help_text = "Identifier (or URI) of the item establishing the interaction.")
    item_to = fields.ForeignKey(ItemResource, 'item_to', full=True, null = True, blank = True, help_text = "Identifier (or URI) of the item receiving the interaction.")
    def build_schema(self):
        base_schema = super(InteractionResource, self).build_schema()
        for f in self._meta.object_class._meta.fields:
            if f.name in base_schema['fields'] and f.choices:
                base_schema['fields'][f.name].update({
                    'choices': [cho[0] for cho in f.choices],
                    })
        return base_schema
    def dehydrate(self, bundle):
        bundle.data['id'] = str(bundle.data['id'])
        bundle.data['owner'] = str(bundle.data['owner'].data['username'])
        bundle.data['taxa_from'] = str(bundle.data['taxa_from'].obj.id)
        bundle.data['taxa_to'] = str(bundle.data['taxa_to'].obj.id)
        if bundle.data['pop_from']:
            bundle.data['pop_from'] = str(bundle.data['pop_from'].obj.id)
        if bundle.data['pop_to']:
            bundle.data['pop_to'] = str(bundle.data['pop_to'].obj.id)
        if bundle.data['item_from']:
            bundle.data['item_from'] = str(bundle.data['item_from'].obj.id)
        if bundle.data['item_to']:
            bundle.data['item_to'] = str(bundle.data['item_to'].obj.id)
        return bundle
    class Meta:
        queryset = Interaction.objects.all()
        authorization = Authorization()
        always_return_data = True
        include_resource_uri = False
        filtering = {
                'owner': ALL_WITH_RELATIONS,
                'taxa_from': ALL_WITH_RELATIONS,
                'taxa_to': ALL_WITH_RELATIONS,
                'pop_to': ALL_WITH_RELATIONS,
                'pop_from': ALL_WITH_RELATIONS,
                'item_to': ALL_WITH_RELATIONS,
                'item_from': ALL_WITH_RELATIONS,
                'ecotype': ALL_WITH_RELATIONS,
                'nature': ALL_WITH_RELATIONS,
                'description': ALL,
                }
        resource_name = 'interaction'
        allowed_methods = ['get','post','patch']

class NetworkResource(ModelResource):
    interactions = fields.ManyToManyField(InteractionResource, 'interactions', full=True, help_text = "List of identifiers (or URIs) of the interactions in the network.")
    environment = fields.ManyToManyField(EnvironmentResource, 'environment', full=True, null=True, blank=True, help_text = "List of identifiers (or URIs) of environmental measurements associated to the network.")
    owner = fields.ForeignKey(UserResource, 'owner', full=True)
    def dehydrate(self, bundle):
        bundle.data['id'] = str(bundle.data['id'])
        bundle.data['interactions'] = [str(inte.data['id']) for inte in bundle.data['interactions']]
        bundle.data['owner'] = str(bundle.data['owner'].data['username'])
        return bundle
    class Meta:
        queryset = Network.objects.all()
        authorization = Authorization()
        always_return_data = True
        include_resource_uri = False
        resource_name = 'network'
        excludes = ['public','owner']
        filtering = {
                'owner': ALL_WITH_RELATIONS,
                'interactions': ALL_WITH_RELATIONS,
                'metaweb': ALL_WITH_RELATIONS,
                'description': ALL,
                'name': ALL,
                'latitude': ALL_WITH_RELATIONS,
                'longitude': ALL_WITH_RELATIONS,
                }
        allowed_methods = ['get','post','patch']

class DatasetResource(ModelResource):
    networks = fields.ManyToManyField(NetworkResource, 'networks', full=True, help_text = "List of identifiers (or URIs) of the networks in the dataset.")
    data = fields.ManyToManyField(RefResource, 'data', full=True, null=True, blank=True, help_text = "List of identifiers (or URIs) of the references describing the data.")
    papers = fields.ManyToManyField(RefResource, 'papers', full=True, null=True, blank=True, help_text = "List of identifiers (or URIs) of the references to the papers associated with the dataset.")
    owner = fields.ForeignKey(UserResource, 'owner', full=True)
    def dehydrate(self, bundle):
        bundle.data['id'] = str(bundle.data['id'])
        bundle.data['networks'] = [str(net.data['id']) for net in bundle.data['networks']]
        bundle.data['papers'] = [str(ref.data['id']) for ref in bundle.data['papers']]
        bundle.data['data'] = [str(ref.data['id']) for ref in bundle.data['data']]
        bundle.data['owner'] = str(bundle.data['owner'].data['username'])
        return bundle
    class Meta:
        queryset = Dataset.objects.all()
        authorization = Authorization()
        always_return_data = True
        include_resource_uri = False
        resource_name = 'dataset'
        filtering = {
                'owner': ALL_WITH_RELATIONS,
                'networks': ALL_WITH_RELATIONS,
                'description': ALL,
                'name': ALL,
                }
        excludes = ['public']
        allowed_methods = ['get','post','patch']
