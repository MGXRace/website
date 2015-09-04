from django.contrib import admin
from .models import Pk3file, Bspfile, Levelshot, Shader, Texture, ShaderReq, BspReq

admin.site.register(Pk3file)
admin.site.register(Bspfile)
admin.site.register(Levelshot)
admin.site.register(Shader)
admin.site.register(Texture)
admin.site.register(ShaderReq)
admin.site.register(BspReq)


# TODO views