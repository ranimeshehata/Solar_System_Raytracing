import numpy as np

from ray_tracing.sphere import Ring
from ray_tracing.vectors import get_sphere_uv, normalize, reflect

def hard_shadow(point, scene, current_sphere, light_sphere):  
    # using the center of the sun as the sample point for shadow calculation
    light_point = light_sphere.center  

    # calculating the direction vector from the surface point to the light source
    light_dir = light_point - point

    # calculate the straight line distance to the light source
    dist_to_light = np.linalg.norm(light_dir)
    if dist_to_light < 1e-4:
        return 0.0 
    # normalize the light direction to use in ray casting
    light_dir = normalize(light_dir)

    #  offset the origin of the shadow ray to avoid self intersection which is the shadow acne
    shadow_origin = point + 1e-4 * light_dir

    # check all objects in the scene to see if any block the light
    for sphere in scene.spheres:
        # skip the current surface sphere and any light emitting spheres because they will not be shaded
        if sphere is current_sphere or sphere.material.emissive:
            continue

        # cast a shadow ray towards the light
        hit_rec = sphere.hit(shadow_origin, light_dir)

        # if the ray hits another object before reaching the light source it's in shadow
        if hit_rec and hit_rec.t < dist_to_light:
            return 0.0  # in shadow light is blocked so we return black for dark shadows

    # if no obstruction is found the point is lighted by this light sample
    return 1.0 



def ray_color(ray_origin, ray_dir, scene, ambient, max_depth, depth=0):
    if depth > max_depth:
        return np.zeros(3, dtype=np.float32)

    hit_record = scene.hit(ray_origin, ray_dir)

    if not hit_record:
        base_col = np.zeros(3, dtype=np.float32)
        
        # nebula effect
        dir = normalize(ray_dir)
        nebula_intensity = 0.3  
        # creating noise patterns using sin function to simulate the cloud form of nebula
        u, v = get_sphere_uv(dir)
        noise1 = np.sin(u * 30 + v * 40) * 0.5 + 0.5  
        noise2 = np.sin(u * 50 - v * 30) * 0.5 + 0.5
        noise3 = np.sin(-u * 20 + v * 60) * 0.5 + 0.5
        
        # applying different colors to each noise channel with different intensities and falloff
        # the exponents to make the colors stand out clearly in the dark
        nebula_blue = np.array([0.2, 0.3, 0.5]) * noise1**3 * nebula_intensity * 0.7
        nebula_purple = np.array([0.4, 0.2, 0.5]) * noise2**4 * nebula_intensity * 0.5
        nebula_red = np.array([0.5, 0.15, 0.2]) * noise3**5 * nebula_intensity * 0.3

        # combined colored noise channels to form the final nebula color
        nebula_col = (nebula_blue + nebula_purple + nebula_red) * 0.7

        if scene.background_texture:
            tex_col = scene.background_texture.value(u, v) 
            # blend the texture background with the nebula
            base_col = tex_col * (1.0 - nebula_intensity*0.5) + nebula_col*255.0
        else:
            base_col = nebula_col * 255.0


        # sun corona calculations
        sun = scene.light
        sun_dir = normalize(sun.center - ray_origin)
        ray_dir_norm = normalize(ray_dir)
        
        # calculate angle between view ray and sun direction
        cos_angle = np.dot(ray_dir_norm, sun_dir)
        angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        
        # calculate sun angular radius
        sun_dist = np.linalg.norm(sun.center - ray_origin)
        sun_angular_radius = np.arcsin(sun.radius / sun_dist)
        
        # corona parameters
        corona_start = sun_angular_radius 
        corona_end = sun_angular_radius * 3.0
        
        if angle < corona_end:
            corona_dist = (angle - corona_start) / (corona_end - corona_start)
            
            if corona_dist < 0:
                pass
            else:
                corona_intensity = np.exp(-corona_dist * 4.0) * (1.0 - corona_dist)
                inner_color = np.array([2.5, 1.8, 1.0])
                outer_color = np.array([0.5, 0.7, 1.2])
                corona_color = inner_color * (1.0 - corona_dist) + outer_color * corona_dist
                
                if corona_dist < 0.8:
                    sun_right = normalize(np.cross(sun_dir, np.array([0, 1, 0])))
                    sun_up = normalize(np.cross(sun_dir, sun_right))
                    ray_angle = np.arctan2(np.dot(ray_dir_norm, sun_up), 
                                          np.dot(ray_dir_norm, sun_right))
                    
                    ray_count = 3
                    ray_factor = (np.sin(ray_angle * ray_count) ** 16) * (1.0 - corona_dist)
                    corona_color += np.array([1.5, 1.2, 0.8]) * ray_factor * 0.5
                
                base_col += corona_color * corona_intensity * 150.0

        return np.clip(base_col, 0.0, 255.0)
    
    # saturn ring shading
    if isinstance(hit_record.sphere, Ring):
        # sample the texture color from the ring material using u and v coordinates at the hit point
        tex_color = hit_record.sphere.material.texture.value(hit_record.u, hit_record.v)

        # normalized direction vectors for lighting and viewing
        light_dir = normalize(scene.light.center - hit_record.point)    # direction from point to light source
        view_dir = normalize(ray_origin - hit_record.point)             # direction from point to camera

        # rim backlight
        # calculate rim lighting to simulate light around edges of the ring
        # 1 - dot(normal, view_dir) gives higher values near edges (when normal is perpendicular to view)
        # raising to the power 3 to make it more focused
        # multiply by factor 0.8 to scale the rim intensity
        rim = max(0.0, 1.0 - np.dot(hit_record.normal, view_dir)) ** 3 * 0.8  

        # specular light
        # calculate half vector between light direction and view direction used in phong model
        half_vec = normalize(light_dir + view_dir)
        spec_angle = max(0.0, np.dot(hit_record.normal, half_vec))  # how aligned the normal is with half vector
        # final specular raised by exponent 64 for more highlight and scaled by material specular strength and 0.5
        specular = spec_angle ** 64 * 0.5 * hit_record.sphere.material.specular_strength  

        # shadow
        # determine shadow strength at the hit point 
        shadow_strength = hard_shadow(hit_record.point, scene, hit_record.sphere, scene.light)
        # smoothen the shadow by scaling
        shadow_strength = shadow_strength ** 0.7 

        # combined light components
        # shaded color affected by ambient light and rim lighting and specular highlights
        shaded_color = tex_color * (ambient + rim + specular)

        # final shaded color by shadow strength and brighten it by 1.2
        shaded_color = shaded_color * shadow_strength * 1.2  

        # glow at edge
        edge_glow = max(0.0, 1.0 - np.dot(hit_record.normal, view_dir)) ** 2 * 0.3
        shaded_color += edge_glow * np.array([1.0, 0.9, 0.8]) 
        return np.clip(shaded_color, 0.0, 255.0)

    # sun
    if hit_record.sphere.material.emissive:
        emitted = hit_record.sphere.material.emitted(hit_record.u, hit_record.v)
        return np.clip(emitted * np.array([1.7, 1.4, 1.1]), 0.0, 255.0) 

    # shading of planets
    tex_color = hit_record.sphere.material.texture.value(hit_record.u, hit_record.v)
    tex_color = enhance_vibrancy(tex_color)
    
    shadow_strength = hard_shadow(hit_record.point, scene, hit_record.sphere, scene.light)
    in_shadow = shadow_strength < 0.1

    if in_shadow:
        # we are in shadow —-> no direct light
        # compute the direction from the surface point to the camera
        view_dir = normalize(-ray_dir)

        # compute rim lighting component
        # this highlights the edges of objects facing away from the camera
        # the dot product is higher when the normal is pointing toward the camera
        # so we raise it to a high power to make the effect more concentrated
        rim = 0.2 * max(0.0, np.dot(hit_record.normal, view_dir)) ** 4

        # ambient light
        ambient_color = ambient * np.array([0.6, 0.7, 1.1])

        # final color in shadow: texture color affected by ambient and rim light
        shaded_color = tex_color * (ambient_color + rim)
    else:
        light_dir = normalize(scene.light.center - hit_record.point)
        half_vec = normalize(light_dir + normalize(-ray_dir))
        
        # diffuse
        diffuse = max(0.0, np.dot(hit_record.normal, light_dir))**2.5
        
        # specular light
        spec_angle = max(0.0, np.dot(hit_record.normal, half_vec))
        specular = hit_record.sphere.material.specular_strength * 3.0 * (spec_angle ** hit_record.sphere.material.shininess)
        specular *= np.array([1.0, 0.9, 0.8])  
        
        # rim lighting for backlight of the sun
        rim = 0.15 * max(0.0, 1.0 - np.dot(hit_record.normal, normalize(-ray_dir)))**4
        
        # combining all lighting components
        shaded_color = tex_color * (diffuse + specular + rim) * np.array([1.1, 1.0, 0.9])
        shaded_color *= shadow_strength  

    return np.clip(shaded_color , 0.0, 255.0)

def enhance_vibrancy(rgb):
    """boost saturation and contrast of the colors to make it more vibrant"""
    hsv = rgb_to_hsv(rgb / 255.0)
    hsv[1] = min(1.0, hsv[1] * 2.0)  # doubling saturation
    hsv[2] = hsv[2]**0.8  # increasing contrast
    rgb = hsv_to_rgb(hsv) * 255.0
    # making red more visible
    if rgb[0] > rgb[1] and rgb[0] > rgb[2]:  
        rgb[0] *= 1.2
    return np.clip(rgb, 0, 255)

def compute_specular(hit_rec, ray_dir, light_dir):
    """
    compute the specular reflection component based on the Phong reflection model.
    """

    # compute the direction in which light would reflect off the surface
    reflect_dir = reflect(-light_dir, hit_rec.normal)

    # compute the direction from the surface point to the camera
    view_dir = normalize(-ray_dir)

    # calculate the angle between the reflection direction and the viewer direction
    # the closer this angle is to 0 the stronger the specular highlight
    spec_angle = max(0.0, np.dot(view_dir, reflect_dir))
    spec_strength = hit_rec.sphere.material.specular_strength * 3.0 
    shininess = hit_rec.sphere.material.shininess * 1.5  

    # compute the final specular component using the Phong specular formula
    spec = spec_strength * (spec_angle ** shininess)

    # add to the specular color warmness due to the orange color of the sun
    return spec * np.array([1.0, 0.9, 0.8])  


# convert an RGB color to HSV (Hue, Saturation, Value) color so that we can adjust the saturation of the color to make it more vibrant
def rgb_to_hsv(rgb):
    rgb = rgb / 255.0
    maxc = np.max(rgb)
    minc = np.min(rgb)
    v = maxc
    if minc == maxc:
        return np.array([0, 0, v])
    s = (maxc-minc) / maxc
    rc = (maxc-rgb[0]) / (maxc-minc)
    gc = (maxc-rgb[1]) / (maxc-minc)
    bc = (maxc-rgb[2]) / (maxc-minc)
    if rgb[0] == maxc:
        h = bc-gc
    elif rgb[1] == maxc:
        h = 2.0+rc-bc
    else:
        h = 4.0+gc-rc
    h = (h/6.0) % 1.0
    return np.array([h, s, v])
# converting back the color to the rgb 
def hsv_to_rgb(hsv):
    h, s, v = hsv
    if s == 0.0:
        return np.array([v, v, v]) * 255.0
    i = int(h*6.0)
    f = (h*6.0) - i
    p = v*(1.0 - s)
    q = v*(1.0 - s*f)
    t = v*(1.0 - s*(1.0-f))
    i = i%6
    if i == 0:
        return np.array([v, t, p]) * 255.0
    if i == 1:
        return np.array([q, v, p]) * 255.0
    if i == 2:
        return np.array([p, v, t]) * 255.0
    if i == 3:
        return np.array([p, q, v]) * 255.0
    if i == 4:
        return np.array([t, p, v]) * 255.0
    if i == 5:
        return np.array([v, p, q]) * 255.0