import re
from maps.shaders import ShaderFileParser


sample_shader = u"""
// blaa

    // blaa blaaa   {
    textures/sfx/flameanim_blue            
     {      

    //*************************************************
    //* Blue Flame *
    //* July 20, 1999 Surface Light 1800 *
    //*Please Comment Changes *
    //*************************************************
        qer_editorimage textures/sfx/b_flame7.tga
    q3map_lightimage textures/sfx/b_flame7.tga
      surfaceparm trans
    surfaceparm nomarks
    surfaceparm nolightmap
     cull none
    q3map_surfacelight 1800
    // texture changed to blue flame.... PAJ
            {

        animMap 10 textures/sfx/b_flame1.tga
        textures/sfx/b_flame2.tga
        textures/sfx/b_flame3.tga
        textures/sfx/b_flame4.tga
        textures/sfx/b_flame5.tga
        textures/sfx/b_flame6.tga
        textures/sfx/b_flame7.tga
        textures/sfx/b_flame8.tga
        blendFunc GL_ONE GL_ONE
        rgbGen wave inverseSawtooth 0 1 0 10

    }

     {   
        animMap 10 textures/sfx/b_flame2.tga
        textures/sfx/b_flame3.tga
        textures/sfx/b_flame4.tga
        textures/sfx/b_flame5.tga
        textures/sfx/b_flame6.tga
        textures/sfx/b_flame7.tga
        textures/sfx/b_flame8.tga
        textures/sfx/b_flame1.tga
        blendFunc GL_ONE GL_ONE
        rgbGen wave sawtooth 0 1 0 10

    }
    lalala
    {

        map textures/sfx/b_flameball.tga
        blendFunc GL_ONE GL_ONE
        rgbGen wave sin .6 .2 0 .6

    }   
    hahaverrassing

  }
   textures/gu3/darkhollow_skybox   
 
 { 
qer_editorimage textures/gu3/darkhollow_view.jpg
surfaceparm noimpact
surfaceparm nolightmap
q3map_globaltexture
surfaceparm sky
q3map_lightsubdivide 256
q3map_sun 1 1 1 100 220 50
q3map_surfacelight 120
 
skyparms env/gu3/darkhollow - -

         }  
    // lalala    
       textures/gu3/cloudy_skybox   
   {
	qer_editorimage textures/gu3/cloudy_bk.tga  
	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_globaltexture
	surfaceparm sky
	q3map_lightsubdivide 2048
	q3map_surfacelight 120
	q3map_sun 1 1 1 100 220 50
	skyparms env/gu3/cloudy - -

}
 
 textures/evil8_base/thrshr_exit 
{
	nopicmip

	{
		map textures/evil8_base/thrshr_exit.jpg
		rgbGen identity

	}
}
textures/coldrun/dfbanner1
{
	nopicmip
	qer_editorimage textures/coldrun/defrag.tga
	q3map_lightimage textures/coldrun/defrag.tga
	q3map_surfacelight 100

	{
		animMap .15 textures/coldrun/defrag.tga textures/coldrun/l33tn355.tga textures/coldrun/defrag_ru.tga
		rgbGen wave sawtooth 0 1 0 .15

	}
	{
		map textures/base_wall/comp3textb.tga
		blendfunc add
		rgbGen wave inversesawtooth 0 1 0 .15
		tcmod scroll 5 .25
	}
	{
		map textures/base_wall/comp3text.tga
		blendfunc add
		rgbGen identity
		tcmod scroll 2 2
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc gl_dst_color gl_zero
	}
	{
		map $lightmap
		tcgen environment
		tcmod scale .5 .5
		rgbGen wave sin .25 0 0 0
		blendfunc add
	}
	//
    } 
     
     //{

  """

sample_shader2 = u"""
textures/sfx/flameanim_blue
{

    //*************************************************
    //* Blue Flame *
    //* July 20, 1999 Surface Light 1800 *
    //*Please Comment Changes *
    //*************************************************
        qer_editorimage textures/sfx/b_flame7.tga
    q3map_lightimage textures/sfx/b_flame7.tga
      surfaceparm trans
    surfaceparm nomarks
    surfaceparm nolightmap
     cull none
    q3map_surfacelight 1800
    // texture changed to blue flame.... PAJ
            {

        animMap 10 textures/sfx/b_flame1.tga
        textures/sfx/b_flame2.tga
        textures/sfx/b_flame3.tga
        textures/sfx/b_flame4.tga
        textures/sfx/b_flame5.tga
        textures/sfx/b_flame6.tga
        textures/sfx/b_flame7.tga
        textures/sfx/b_flame8.tga
        blendFunc GL_ONE GL_ONE
        rgbGen wave inverseSawtooth 0 1 0 10

    }

     {   
        animMap 10 textures/sfx/b_flame2.tga
        textures/sfx/b_flame3.tga
        textures/sfx/b_flame4.tga
        textures/sfx/b_flame5.tga
        textures/sfx/b_flame6.tga
        textures/sfx/b_flame7.tga
        textures/sfx/b_flame8.tga
        textures/sfx/b_flame1.tga
        blendFunc GL_ONE GL_ONE
        rgbGen wave sawtooth 0 1 0 10

    }
    {

        map textures/sfx/b_flameball.tga
        blendFunc GL_ONE GL_ONE
        rgbGen wave sin .6 .2 0 .6

    }
}
textures/gu3/darkhollow_skybox
{
qer_editorimage textures/gu3/darkhollow_view.jpg
surfaceparm noimpact
surfaceparm nolightmap
q3map_globaltexture
surfaceparm sky
q3map_lightsubdivide 256
q3map_sun 1 1 1 100 220 50
q3map_surfacelight 120

skyparms env/gu3/darkhollow - -
}
textures/gu3/cloudy_skybox
{
	qer_editorimage textures/gu3/cloudy_bk.tga  
	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_globaltexture
	surfaceparm sky
	q3map_lightsubdivide 2048
	q3map_surfacelight 120
	q3map_sun 1 1 1 100 220 50
	skyparms env/gu3/cloudy - -

}
textures/evil8_base/thrshr_exit
{
nopicmip
	{
		map textures/evil8_base/thrshr_exit.jpg
		rgbGen identity
	}
}
textures/coldrun/dfbanner1
{
	nopicmip
	qer_editorimage textures/coldrun/defrag.tga
	q3map_lightimage textures/coldrun/defrag.tga
	q3map_surfacelight 100

	{
		animMap .15 textures/coldrun/defrag.tga textures/coldrun/l33tn355.tga textures/coldrun/defrag_ru.tga
		rgbGen wave sawtooth 0 1 0 .15

	}
	{
		map textures/base_wall/comp3textb.tga
		blendfunc add
		rgbGen wave inversesawtooth 0 1 0 .15
		tcmod scroll 5 .25
	}
	{
		map textures/base_wall/comp3text.tga
		blendfunc add
		rgbGen identity
		tcmod scroll 2 2
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc gl_dst_color gl_zero
	}
	{
		map $lightmap
		tcgen environment
		tcmod scale .5 .5
		rgbGen wave sin .25 0 0 0
		blendfunc add
	}
}
"""





def get_shaders_regex(shaderfile):
    # shaderfile = u"\n".join(_sanitize(shaderfile))
    shaderRegex = re.compile('^([^\r\n}][^/][^/](?:\S+/)+[^\r\n]+)$', re.I | re.M )
    startPos = shaderRegex.search(shaderfile).start()
    splitShader = shaderRegex.split(shaderfile[startPos:])
    texregex = re.compile('((?:\S+/)+[^ ]+\.(?:tga|jpg))', re.I | re.M )
    shaders = []
    for i in range(1, len(splitShader), 2):
        textures = texregex.findall(splitShader[i+1])
        shaders.append({splitShader[i]: textures})
    return shaders

# parsed_shaders = get_shaders(sample_shader)
# parsed_shaders_regex = get_shaders_regex(sample_shader)
# parsed_shaders_regex2 = get_shaders_regex(sample_shader2)

# pretty_print(parsed_shaders)
# print parsed_shaders_regex
# print parsed_shaders_regex2

parser = ShaderFileParser(sample_shader)
parser.pretty_print()

reqs = parser.get_texture_requirements()
print reqs
