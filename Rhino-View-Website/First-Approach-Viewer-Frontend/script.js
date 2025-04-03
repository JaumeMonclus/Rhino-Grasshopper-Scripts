// #region IMPORTS //

import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import { Rhino3dmLoader } from 'three/examples/jsm/loaders/3DMLoader'

// #endregion IMPORTS //

// #region GLOBALS //

const loader = new Rhino3dmLoader()
loader.setLibraryPath( 'https://unpkg.com/rhino3dm@8.4.0/' )

const upload = document.getElementById("file-upload")

const material = new THREE.MeshPhysicalMaterial();

material.color = new THREE.Color(0xb0b0b0); // o material.color.set(0xb0b0b0);
material.metalness = 0.80;
material.roughness = 0.3;
material.clearcoat= 0.5;
material.clearcoatRoughness= 0.25;
material.envMapIntensity = 1.5;
material.transparent= true;
material.opacity= 0.85; // 50% transparente
material.flatShading = true;

const raycaster = new THREE.Raycaster();


let renderer, scene, camera, controls;

// #endregion GLOBALS //

// #region EVENTS //

upload.addEventListener('change', function () {
    if (this.files && this.files[0]) {
        showSpinner(true)
        const file = this.files[0]

        const reader = new FileReader()

        reader.readAsArrayBuffer(file)

        reader.addEventListener('load', function (e) {
            const arr = new Uint8Array(e.target.result).buffer

            loader.parse(arr, (object) => {
                
                // hide spinner
                showSpinner(false);
                // console.log(object)


                // recorrer los objetos i aplicar el material

                object.traverse(child => {
                    if(child.isMesh){
                        child.material = material;
                        child.castShadow = true;
                        child.receiveShadow = true;
                    }
                });

                //clear objects from scene
                scene.traverse(child => {
                    if (child.userData.hasOwnProperty( 'objectType' ) && child.userData.objectType === 'File3dm' ) {
                        scene.remove(child)
                    }
                });

                //add doc to scene
                scene.add(object)

                // zoom to extents
                zoomCameraToSelection(camera, controls, [object])

                //animate()

            }, (error) => {
                console.log( error )
            } )
        })

    }
})

// #endregion EVENTS //

// #region INIT //

init()
animate()

function init() {

    // Rhino models are z-up, so set this as the default
    THREE.Object3D.DEFAULT_UP = new THREE.Vector3(0, 0, 1)

    //renderer

    renderer = new THREE.WebGLRenderer({ antialias: true })
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.setPixelRatio(window.devicePixelRatio)
    renderer.setSize(window.innerWidth, window.innerHeight)
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.outputEncoding = THREE.sRGBEncoding;
    renderer.toneMappingExposure = 1.0; 

    document.getElementById('container').appendChild(renderer.domElement)


    //scene

    // create a scene and a camera
    scene = new THREE.Scene()
    scene.background = new THREE.Color(0.8, 0.8, 0.8)


    //camera

    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000)
    camera.position.set(0,0,5)

    //controls
    controls = new OrbitControls(camera, renderer.domElement)

    // add a directional light
    const directionalLight = new THREE.DirectionalLight(new THREE.Color(0x888888), 15);
    directionalLight.position.set(10, 10, 10);
    directionalLight.castShadow = false ; // sombras activadas
    directionalLight.target.position.set( 0, 0, 0 );
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    scene.add(directionalLight);
    scene.add(directionalLight.target);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
    ambientLight.intensity = 0.2;

    scene.add(ambientLight);

    const sphereGeo = new THREE.SphereGeometry(4, 20, 20)
    const sphere = new THREE.Mesh(sphereGeo, new THREE.MeshNormalMaterial)
    //scene.add( sphere )


    // #add a floor

    const planeGeometry = new THREE.PlaneGeometry(10000, 10000);
    const planeMaterial = new THREE.ShadowMaterial({ opacity: 0.8 });
    const plane = new THREE.Mesh(planeGeometry, planeMaterial);
    plane.receiveShadow = true;
    plane.position.set(0, 0, 0);
    plane.userData.ignoreRaycast = true;
    scene.add(plane);

    // handle changes in the window size
    window.addEventListener('resize', onWindowResize, false)

}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight
    camera.updateProjectionMatrix()
    renderer.setSize(window.innerWidth, window.innerHeight)
}

// function to continuously render the scene
function animate() {

    requestAnimationFrame(animate)
    renderer.render(scene, camera)

}

// #endregion INIT //

// #region UTILITY //

/**
 * Shows or hides the loading spinner
 */
function showSpinner(enable) {
    if (enable)
        document.getElementById('loader').style.display = 'block'
    else
        document.getElementById('loader').style.display = 'none'
}

/**
 * Helper function that behaves like rhino's "zoom to selection", but for three.js!
 */

function zoomCameraToSelection(camera, controls, selection, fitOffset = 1.1) {

    const box = new THREE.Box3();

    for (const object of selection) {
        if (object.isLight) continue
        box.expandByObject(object);
    }

    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());

    const maxSize = Math.max(size.x, size.y, size.z);
    const fitHeightDistance = maxSize / (2 * Math.atan(Math.PI * camera.fov / 360));
    const fitWidthDistance = fitHeightDistance / camera.aspect;
    const distance = fitOffset * Math.max(fitHeightDistance, fitWidthDistance);

    const direction = controls.target.clone()
        .sub(camera.position)
        .normalize()
        .multiplyScalar(distance);
    controls.maxDistance = distance * 10;
    controls.target.copy(center);

    camera.near = distance / 100;
    camera.far = distance * 100;
    camera.updateProjectionMatrix();
    camera.position.copy(controls.target).sub(direction);

    controls.update();

}

// #endregion UTILITY //


// #begginign region raycasting //

let selectedObject = null;

document.addEventListener('mousedown', onMouseDown);

function onMouseDown(event) {
     // Obtén el bounding rect del canvas (renderer.domElement)
     const rect = renderer.domElement.getBoundingClientRect();
     const coords = new THREE.Vector2(
         ((event.clientX - rect.left) / rect.width) * 2 - 1,
         -(((event.clientY - rect.top) / rect.height) * 2 - 1)
     );
     
    raycaster.setFromCamera(coords, camera);

    const intersections = raycaster.intersectObject(scene, true)
        .filter(intersection => !intersection.object.userData.ignoreRaycast);

    if (intersections.length > 0) {
        const newSelected = intersections[0].object;
    
        if  ( selectedObject && selectedObject !== newSelected){
            if (selectedObject.userData.originalMaterial){
                selectedObject.material = selectedObject.userData.originalMaterial;
            }
        }

        if (!newSelected.userData.originalMaterial){
            newSelected.userData.originalMaterial = newSelected.material;
        }

        const randomColor = new THREE.Color(56/255, 12/255, 28/255);
                
        newSelected.material = new THREE.MeshBasicMaterial({ color: randomColor });

        selectedObject = newSelected;

        console.log(`${selectedObject.name} was clicked!`);
        console.log(selectedObject.userData.attributes.userStrings); 
        
        updateUserSettingsPanel(newSelected);
        }
        else  {
            if ( selectedObject){
                selectedObject.material = selectedObject.userData.originalMaterial;
                selectedObject = null;
            }
        }
}
// #endregion raycasting //

// #region extracting attributes//

function updateUserSettingsPanel(object) {
    // 1. Se inicia la variable "html" mostrando el nombre del objeto o "Sin nombre" si no existe.
    // let html = `<p><strong>Nombre:</strong> ${object.userData.attributes.userStrings.Name || 'Sin nombre'}</p>`;
    
    // 2. Se añade el UUID del objeto.
    let html = `<p><strong>UUID:</strong> ${object.uuid}</p>`;
    // console.log( object.userData.attributes.userStrings)
    // 3. Verificamos que en userData exista la propiedad attributes y, dentro de ella, el array userStrings.
    if (
      object.userData && 
      object.userData.attributes && 
      object.userData.attributes.userStrings && 
      object.userData.attributes.userStrings.length > 0
    ) {
      // 4. Iteramos sobre cada par en el array userStrings.
      object.userData.attributes.userStrings.forEach(setting => {
        // Cada "setting" es un array con dos elementos: [clave, valor].
        html += `<p><strong>${setting[0]}:</strong> ${setting[1]}</p>`;
      });
    } else {
      // 5. Si no se encuentran userStrings, se muestra un mensaje.
      html += `<p>No se encontraron 'userStrings'.</p>`;
    }
    
    // 6. Se actualiza el contenido del panel lateral.
    document.getElementById("objectproperties").innerHTML = html;
  }
  
  
// #end region extracting attributes//

// region searching objects by name 

// Define la función searchAllObjs antes de usarla
function searchAllObjs(query) {
    let results = "";
    const lowerQuery = query.toLowerCase();
  
    // Recorre todos los objetos de la escena
    scene.traverse(child => {
      if (child.isMesh && 
          child.userData &&
          child.userData.attributes &&
          child.userData.attributes.userStrings &&
          child.userData.attributes.userStrings.length > 0) {
        
        // Suponiendo que el primer par es [ "Name", <value> ]
        const namePair = child.userData.attributes.userStrings[0];
        if (namePair && namePair.length >= 2 && namePair[1].toLowerCase().includes(lowerQuery)) {
          results += `<p><strong>There is an object with this ID</p>`;
        }
      }
    });
    
    if (results === "") {
      results = `<p>No coincidence found.</p>`;
    }
    return results;
  }
  
  // Luego el event listener:
  document.getElementById('search-input').addEventListener('keydown', (event) => {
    if (event.key === "Enter") {
      const query = event.target.value;
      console.log("Query:", query);
      const resultHTML = searchAllObjs(query); // Llama a la función definida
      console.log("Result HTML:", resultHTML);
      document.getElementById('searchresults').innerHTML = resultHTML;
    }
  });