from rest_framework.routers import SimpleRouter
from .views import (
    Authentication, 
    )

router = SimpleRouter()
router.register('auth', Authentication, basename='auth')
urlpatterns = router.urls
