import numpy as np

from ray_tracing.vectors import random_point_on_sphere,normalize, reflect


def soft_shadow(point, scene, current_sphere, light_sphere, num_samples=50):
    shadow_count = 0
    for _ in range(num_samples):
        light_point = random_point_on_sphere(light_sphere.center, light_sphere.radius)
        light_dir = light_point - point
        dist_to_light = np.linalg.norm(light_dir)
        if dist_to_light < 1e-4:
            continue
        light_dir = normalize(light_dir)
        shadow_origin = point + 1e-4 * light_dir
        blocked = False
        for sphere in scene.spheres:
            if sphere is current_sphere or sphere.material.emissive:
                continue
            hit_rec = sphere.hit(shadow_origin, light_dir)
            if hit_rec and hit_rec.t < dist_to_light:
                blocked = True
                break
        shadow_count += blocked
    visibility = 1 - (shadow_count / num_samples)
    return visibility ** 3

def ray_color(ray_origin, ray_dir, scene, ambient):
    hit_record = scene.hit(ray_origin, ray_dir)
    if not hit_record:
        return np.zeros(3, dtype=np.float32)
    if hit_record.sphere.material.emissive:
        return hit_record.sphere.material.emitted(hit_record.u, hit_record.v)
    shadow_factor = soft_shadow(
        hit_record.point, scene, hit_record.sphere, scene.light
    )
    light_dir = normalize(scene.light.center - hit_record.point)
    normal = hit_record.normal
    view_dir = normalize(-ray_dir)
    diffuse = max(0.0, np.dot(normal, light_dir))
    reflect_dir = reflect(-light_dir, normal)
    spec_angle = max(0.0, np.dot(view_dir, reflect_dir))
    material = hit_record.sphere.material
    specular = material.specular_strength * (spec_angle ** material.shininess)
    direct_light = (diffuse + specular) * shadow_factor
    intensity = ambient + direct_light
    tex_color = material.texture.value(hit_record.u, hit_record.v)
    return np.clip(tex_color * intensity, 0, 255)