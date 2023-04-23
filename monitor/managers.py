from django.db import models

class MonitorManager(models.Manager):
    '''
    Manager for the Monitor Class
    '''
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
    
    def uptime_candidates(self):
        return self.get_queryset().filter(test_uptime=True)
    
    def port_candidates(self):
        return self.get_queryset().filter(test_port=True)    
    
    def ssl_candidates(self):
        return self.get_queryset().filter(test_ssl=True)
    
    def speed_candidates(self):
        return self.get_queryset().filter(test_speed=True)
