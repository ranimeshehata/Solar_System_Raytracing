# Course Project: Solar System Ray Tracing

## Objective
Apply computer graphics and ray tracing techniques to render a single high-quality scene of the Solar System at a given simulation time `t`, from a specified camera position, camera orientation, and up vector.

## Team Members and Task Split

### Team Member 1: **Ray Tracing** (since it is the core, I left it alone)
- **Ray-Sphere Intersection**
  - Implement ray-object intersection (planets, Moon, Sun modeled as spheres)
- **Basic Ray Tracing Engine**
  - Set up the ray tracing loop and rendering logic

### Team Member 2: **Lighting + Sun Emission + Camera Setup**
- **Lighting Models**
  - Implement ambient, diffuse, and specular lighting (Phong or Blinn-Phong model)
- **Sun Emission**
  - Simulate the Sun as an emissive light source
- **Global Illumination & Shading**
  - Integrate light interaction (shading calculations)
- **Camera Setup**
  - Handle camera position `(x, y, z)`
  - Implement look-at target and up vector
  - Generate primary rays from camera

### Team Member 3: **Textures + Orbits + Effects**
- **Textures**
  - Apply texture mapping to planets and Moon (use NASA textures or similar)
- **Orbital & Rotational Transformations**
  - Compute positions and rotations of planets and Moon at simulation time `t`
- **Visual Effects & Skybox (Bonus)**
  - Implement optional effects like atmospheric scattering, Sun's glow
  - Add skybox (background starfield or galaxy)

> **Note:** The textures included in this project are from [Solar System Scope Textures](https://www.solarsystemscope.com/textures/) and are **not sourced from NASA**.
> You are welcome to replace them with publicly available NASA textures if you prefer higher accuracy or realism.

## Bonus Features
- **Skybox** (Team Member 3)
- **Atmospheric Scattering / Sun’s Glow** (Team Member 2)
- **Real-time or Semi-real-time Renderer** (Collaborative, optional)


## Resources
- [**OpenGl Playlist**](https://youtu.be/bmCYgoCAyMQ?si=TPFQyBV041nCOI2d) – The GitHub repository for the code is available in the video description.
- [**Solar System Simulator**](https://www.solarsystemscope.com/)