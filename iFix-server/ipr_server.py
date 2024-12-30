import falcon

# from patch_resource import PatchResource
from exclude_group import ExcludeGroupResource
from explore_group import ExploreGroupResource
from repair_service import RepairService
from session_resource import SessionResource
from instrument_resource import InstrumentResource

server = application = falcon.App(cors_enable=True)

service = RepairService()
# app.add_route('/patches/{id}', PatchResource())
server.add_route('/session', SessionResource(service))
server.add_route('/explore_group', ExploreGroupResource(service))
server.add_route('/exclude_group', ExcludeGroupResource(service))
server.add_route('/mock_instrument', InstrumentResource(service))
