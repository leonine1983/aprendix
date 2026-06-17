// ============================================
// RiverSystem.js - Sistema Procedural de Rios
// Versão: 1.0.0
// Módulo independente e modular
// ============================================

import * as THREE from 'three';

export class RiverSystem {
    constructor(scene, terrainData) {
        this.scene = scene;
        this.terrainData = terrainData;
        this.rivers = [];
        this.waterfalls = [];
        this.lakes = [];
        this.flowField = null;
        this.riverMeshes = [];
        this.materials = this.createMaterials();
        this.isEnabled = true;
        this.animationTime = 0;
        
        console.log('🌊 RiverSystem initialized');
    }

    // ============================================
    // MATERIAIS
    // ============================================
    createMaterials() {
        return {
            water: new THREE.MeshPhysicalMaterial({
                color: 0x4fc3f7,
                roughness: 0.1,
                metalness: 0.3,
                transmission: 0.6,
                thickness: 1,
                transparent: true,
                opacity: 0.85,
                clearcoat: 1.0,
                ior: 1.33,
                side: THREE.DoubleSide
            }),
            riverbed: new THREE.MeshStandardMaterial({
                color: 0x5d4037,
                roughness: 0.95,
                metalness: 0.0
            }),
            wetRock: new THREE.MeshStandardMaterial({
                color: 0x3e2723,
                roughness: 0.7,
                metalness: 0.1
            }),
            waterfall: new THREE.MeshPhysicalMaterial({
                color: 0x81d4fa,
                roughness: 0.1,
                metalness: 0.3,
                transmission: 0.7,
                thickness: 0.5,
                transparent: true,
                opacity: 0.85,
                clearcoat: 1.0,
                side: THREE.DoubleSide,
                emissive: 0x81d4fa,
                emissiveIntensity: 0.2
            })
        };
    }

    // ============================================
    // FLOW FIELD
    // ============================================
    generateFlowField() {
        if (!this.terrainData || !this.terrainData.heightmap) {
            console.warn('RiverSystem: Terrain data not available');
            return null;
        }

        const { width, height, heightmap, resolution } = this.terrainData;
        const flowField = new Array(width * height);

        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const idx = y * width + x;
                const currentHeight = heightmap[idx];

                const neighbors = [
                    { dx: -1, dy: -1 }, { dx: 0, dy: -1 }, { dx: 1, dy: -1 },
                    { dx: -1, dy: 0 },                      { dx: 1, dy: 0 },
                    { dx: -1, dy: 1 },  { dx: 0, dy: 1 },  { dx: 1, dy: 1 }
                ];

                let minNeighborHeight = currentHeight;
                let minNeighborIdx = idx;

                for (const n of neighbors) {
                    const nx = x + n.dx;
                    const ny = y + n.dy;
                    
                    if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
                        const nIdx = ny * width + nx;
                        const nHeight = heightmap[nIdx];
                        
                        if (nHeight < minNeighborHeight) {
                            minNeighborHeight = nHeight;
                            minNeighborIdx = nIdx;
                        }
                    }
                }

                if (minNeighborIdx !== idx) {
                    const nx = minNeighborIdx % width;
                    const ny = Math.floor(minNeighborIdx / width);
                    const dx = (nx - x) / resolution;
                    const dy = (ny - y) / resolution;
                    const length = Math.sqrt(dx * dx + dy * dy);
                    
                    flowField[idx] = {
                        x: dx / length,
                        y: dy / length,
                        slope: (currentHeight - minNeighborHeight) / resolution
                    };
                } else {
                    flowField[idx] = { x: 0, y: 0, slope: 0 };
                }
            }
        }

        this.flowField = flowField;
        console.log('🌊 Flow field generated');
        return flowField;
    }

    // ============================================
    // NASCENTES
    // ============================================
    findSources(minHeight = 0.7, maxSources = 3) {
        if (!this.terrainData || !this.terrainData.heightmap) return [];

        const { width, height, heightmap, resolution } = this.terrainData;
        const sources = [];

        for (let y = 2; y < height - 2; y++) {
            for (let x = 2; x < width - 2; x++) {
                const idx = y * width + x;
                const h = heightmap[idx];

                if (h < minHeight) continue;

                let isPeak = true;
                for (let dy = -2; dy <= 2; dy++) {
                    for (let dx = -2; dx <= 2; dx++) {
                        if (dx === 0 && dy === 0) continue;
                        const nIdx = (y + dy) * width + (x + dx);
                        if (heightmap[nIdx] > h) {
                            isPeak = false;
                            break;
                        }
                    }
                    if (!isPeak) break;
                }

                if (isPeak) {
                    sources.push({
                        x: (x - width / 2) * resolution,
                        z: (y - height / 2) * resolution,
                        height: h,
                        idx: idx
                    });
                }
            }
        }

        sources.sort((a, b) => b.height - a.height);
        console.log(`🏔️ Found ${sources.length} river sources`);
        return sources.slice(0, maxSources);
    }

    // ============================================
    // RASTREAR CAMINHO
    // ============================================
    traceRiverPath(sourceIdx) {
        if (!this.flowField || !this.terrainData) return [];

        const { width, height, heightmap, resolution } = this.terrainData;
        const path = [];
        let currentIdx = sourceIdx;
        const visited = new Set();
        let steps = 0;
        const maxSteps = width * height;

        while (steps < maxSteps) {
            if (visited.has(currentIdx)) break;
            visited.add(currentIdx);

            const x = currentIdx % width;
            const y = Math.floor(currentIdx / width);
            const worldX = (x - width / 2) * resolution;
            const worldZ = (y - height / 2) * resolution;
            const height = heightmap[currentIdx];

            path.push({
                x: worldX,
                y: height,
                z: worldZ,
                idx: currentIdx
            });

            if (height <= 0.05) break;

            const flow = this.flowField[currentIdx];
            if (!flow || (flow.x === 0 && flow.y === 0)) break;

            const nextX = Math.round(x + flow.x * resolution);
            const nextY = Math.round(y + flow.y * resolution);

            if (nextX < 0 || nextX >= width || nextY < 0 || nextY >= height) break;

            currentIdx = nextY * width + nextX;
            steps++;
        }

        console.log(`🌊 River path traced: ${path.length} points`);
        return path;
    }

    // ============================================
    // SUAVIZAR CAMINHO
    // ============================================
    smoothPath(path, smoothness = 0.5) {
        if (path.length < 3) return path;

        const points = path.map(p => new THREE.Vector3(p.x, p.y + 0.1, p.z));
        const smoothedPoints = [];

        for (let i = 0; i < points.length - 1; i++) {
            smoothedPoints.push(points[i]);
            
            const p1 = points[i];
            const p2 = points[i + 1];
            const mid = new THREE.Vector3().lerpVectors(p1, p2, 0.5);
            
            mid.x += (Math.random() - 0.5) * smoothness;
            mid.z += (Math.random() - 0.5) * smoothness;
            
            smoothedPoints.push(mid);
        }
        smoothedPoints.push(points[points.length - 1]);

        return smoothedPoints;
    }

    // ============================================
    // CRIAR MESH DO RIO
    // ============================================
    createRiverMesh(path, width = 2) {
        if (path.length < 2) return null;

        const curve = new THREE.CatmullRomCurve3(path, false, 'catmullrom', 0.5);
        const segments = Math.max(path.length * 4, 50);
        const points = curve.getPoints(segments);
        
        const geometry = new THREE.BufferGeometry();
        const vertices = [];
        const uvs = [];
        const indices = [];

        for (let i = 0; i < points.length; i++) {
            const point = points[i];
            const t = i / (points.length - 1);
            
            let tangent;
            if (i < points.length - 1) {
                tangent = new THREE.Vector3().subVectors(points[i + 1], point).normalize();
            } else {
                tangent = new THREE.Vector3().subVectors(point, points[i - 1]).normalize();
            }
            
            const normal = new THREE.Vector3(0, 1, 0);
            const binormal = new THREE.Vector3().crossVectors(tangent, normal).normalize();
            
            const localWidth = width * (0.5 + t * 0.5);
            
            const left = new THREE.Vector3().copy(point).addScaledVector(binormal, -localWidth / 2);
            const right = new THREE.Vector3().copy(point).addScaledVector(binormal, localWidth / 2);
            
            left.y += 0.05;
            right.y += 0.05;
            
            vertices.push(left.x, left.y, left.z);
            vertices.push(right.x, right.y, right.z);
            
            uvs.push(0, t);
            uvs.push(1, t);
            
            if (i < points.length - 1) {
                const base = i * 2;
                indices.push(base, base + 1, base + 2);
                indices.push(base + 1, base + 3, base + 2);
            }
        }

        geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
        geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
        geometry.setIndex(indices);
        geometry.computeVertexNormals();

        const mesh = new THREE.Mesh(geometry, this.materials.water);
        mesh.receiveShadow = true;
        
        return { mesh, curve, points };
    }

    // ============================================
    // CRIAR CACHOEIRA
    // ============================================
    createWaterfall(position, height = 5, width = 3) {
        const group = new THREE.Group();
        group.position.copy(position);

        const channelGeo = new THREE.BoxGeometry(width, height, width * 0.5);
        const channel = new THREE.Mesh(channelGeo, this.materials.wetRock);
        channel.position.y = -height / 2;
        channel.castShadow = true;
        group.add(channel);

        const waterGeo = new THREE.PlaneGeometry(width * 0.85, height, 8, 32);
        const water = new THREE.Mesh(waterGeo, this.materials.waterfall);
        water.position.set(0, -height / 2, width * 0.25 + 0.3);
        group.add(water);

        const particleCount = 600;
        const particleGeo = new THREE.BufferGeometry();
        const particlePos = new Float32Array(particleCount * 3);
        const particleVel = new Float32Array(particleCount);

        for (let i = 0; i < particleCount; i++) {
            particlePos[i * 3] = (Math.random() - 0.5) * width * 0.8;
            particlePos[i * 3 + 1] = -height + Math.random() * height;
            particlePos[i * 3 + 2] = width * 0.25 + 0.3 + (Math.random() - 0.5) * width * 0.5;
            particleVel[i] = 0.3 + Math.random() * 0.5;
        }

        particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePos, 3));
        particleGeo.setAttribute('velocity', new THREE.BufferAttribute(particleVel, 1));

        const particleMat = new THREE.PointsMaterial({
            color: 0xb3e5fc,
            size: 0.5,
            transparent: true,
            opacity: 0.9,
            blending: THREE.AdditiveBlending
        });

        const particles = new THREE.Points(particleGeo, particleMat);
        group.add(particles);

        const mistCount = 150;
        const mistGeo = new THREE.BufferGeometry();
        const mistPos = new Float32Array(mistCount * 3);
        for (let i = 0; i < mistCount; i++) {
            mistPos[i * 3] = (Math.random() - 0.5) * width * 3;
            mistPos[i * 3 + 1] = -height + Math.random() * 5;
            mistPos[i * 3 + 2] = width * 0.25 + 2 + (Math.random() - 0.5) * width * 1.5;
        }
        mistGeo.setAttribute('position', new THREE.BufferAttribute(mistPos, 3));
        
        const mistMat = new THREE.PointsMaterial({
            color: 0xffffff,
            size: 2,
            transparent: true,
            opacity: 0.5,
            blending: THREE.AdditiveBlending
        });
        
        const mist = new THREE.Points(mistGeo, mistMat);
        group.add(mist);

        this.scene.add(group);

        return {
            group,
            particles,
            particleGeo,
            particleVel,
            particleCount,
            mist,
            height,
            width
        };
    }

    // ============================================
    // CRIAR LAGO
    // ============================================
    createLake(center, radius = 5, depth = 1) {
        const lakeGeo = new THREE.CircleGeometry(radius, 32);
        lakeGeo.rotateX(-Math.PI / 2);
        
        const lake = new THREE.Mesh(lakeGeo, this.materials.water);
        lake.position.copy(center);
        lake.position.y += 0.05;
        lake.receiveShadow = true;
        
        this.scene.add(lake);
        this.lakes.push(lake);
        
        console.log(`🏞️ Lake created at (${center.x}, ${center.z})`);
        return lake;
    }

    // ============================================
    // DETECTAR LAGOS
    // ============================================
    detectAndCreateLakes(path) {
        if (!this.terrainData || !this.terrainData.heightmap) return;

        const { width, height, heightmap, resolution } = this.terrainData;
        
        for (let i = 10; i < path.length - 10; i += 20) {
            const point = path[i];
            const x = Math.round((point.x / resolution) + width / 2);
            const z = Math.round((point.z / resolution) + height / 2);
            
            if (x < 5 || x >= width - 5 || z < 5 || z >= height - 5) continue;

            let isDepression = true;
            const centerHeight = heightmap[z * width + x];
            
            for (let dz = -3; dz <= 3; dz++) {
                for (let dx = -3; dx <= 3; dx++) {
                    if (dx === 0 && dz === 0) continue;
                    const h = heightmap[(z + dz) * width + (x + dx)];
                    if (h < centerHeight - 0.1) {
                        isDepression = false;
                        break;
                    }
                }
                if (!isDepression) break;
            }

            if (isDepression && Math.random() > 0.7) {
                this.createLake(
                    new THREE.Vector3(point.x, point.y, point.z),
                    3 + Math.random() * 3,
                    0.5
                );
            }
        }
    }

    // ============================================
    // GERAR RIO COMPLETO
    // ============================================
    generateRiver(sourceIdx, width = 2) {
        this.clearRivers();

        const path = this.traceRiverPath(sourceIdx);
        if (path.length < 5) {
            console.warn('RiverSystem: Path too short');
            return null;
        }

        const smoothedPath = this.smoothPath(path);
        const riverData = this.createRiverMesh(smoothedPath, width);
        if (!riverData) return null;

        this.scene.add(riverData.mesh);
        this.riverMeshes.push(riverData.mesh);

        const lastPoints = path.slice(-5);
        const heightDrop = lastPoints[0].y - lastPoints[lastPoints.length - 1].y;
        
        let waterfall = null;
        if (heightDrop > 3) {
            const lastPoint = path[path.length - 1];
            waterfall = this.createWaterfall(
                new THREE.Vector3(lastPoint.x, lastPoint.y, lastPoint.z),
                Math.min(heightDrop, 10),
                width
            );
            this.waterfalls.push(waterfall);
        }

        this.detectAndCreateLakes(path);

        const river = {
            path: smoothedPath,
            mesh: riverData.mesh,
            curve: riverData.curve,
            waterfall,
            sourceIdx
        };

        this.rivers.push(river);
        console.log('✅ River generated successfully');
        return river;
    }

    // ============================================
    // ATUALIZAR RIOS
    // ============================================
    updateRivers() {
        if (!this.isEnabled) return;

        console.log('🔄 Updating rivers...');
        this.generateFlowField();
        const sources = this.findSources();
        this.clearRivers();

        for (const source of sources) {
            this.generateRiver(source.idx);
        }
    }

    // ============================================
    // LIMPAR RIOS
    // ============================================
    clearRivers() {
        for (const mesh of this.riverMeshes) {
            this.scene.remove(mesh);
            mesh.geometry.dispose();
        }
        this.riverMeshes = [];

        for (const wf of this.waterfalls) {
            this.scene.remove(wf.group);
            wf.particleGeo.dispose();
        }
        this.waterfalls = [];

        for (const lake of this.lakes) {
            this.scene.remove(lake);
            lake.geometry.dispose();
        }
        this.lakes = [];

        this.rivers = [];
    }

    // ============================================
    // ANIMAÇÃO
    // ============================================
    animate(deltaTime) {
        this.animationTime += deltaTime;

        for (const wf of this.waterfalls) {
            const positions = wf.particleGeo.attributes.position.array;
            const velocities = wf.particleVel;

            for (let i = 0; i < wf.particleCount; i++) {
                positions[i * 3 + 1] -= velocities[i];
                
                if (positions[i * 3 + 1] < -wf.height) {
                    positions[i * 3] = (Math.random() - 0.5) * wf.width * 0.8;
                    positions[i * 3 + 1] = 0;
                    positions[i * 3 + 2] = wf.width * 0.25 + 0.3 + (Math.random() - 0.5) * wf.width * 0.5;
                }
            }
            wf.particleGeo.attributes.position.needsUpdate = true;

            const mistPos = wf.mist.geometry.attributes.position.array;
            for (let i = 0; i < mistPos.length; i += 3) {
                mistPos[i] += Math.sin(this.animationTime * 2 + i) * 0.05;
                mistPos[i + 1] += Math.cos(this.animationTime * 1.5 + i) * 0.03;
                mistPos[i + 2] += Math.sin(this.animationTime * 1.8 + i) * 0.04;

                if (mistPos[i + 1] > 5) {
                    mistPos[i + 1] = -wf.height + Math.random() * 3;
                }
            }
            wf.mist.geometry.attributes.position.needsUpdate = true;
        }

        for (const mesh of this.riverMeshes) {
            const positions = mesh.geometry.attributes.position.array;
            for (let i = 0; i < positions.length; i += 3) {
                positions[i + 1] += Math.sin(this.animationTime * 2 + positions[i] * 0.5) * 0.002;
            }
            mesh.geometry.attributes.position.needsUpdate = true;
        }
    }

    // ============================================
    // HOOKS
    // ============================================
    onMountainMoved() {
        console.log('🏔️ Mountain moved, updating rivers...');
        this.updateRivers();
    }

    onTerrainModified() {
        console.log('🗺️ Terrain modified, updating rivers...');
        this.updateRivers();
    }

    setEnabled(enabled) {
        this.isEnabled = enabled;
        if (!enabled) {
            this.clearRivers();
        } else {
            this.updateRivers();
        }
    }

    // ============================================
    // SERIALIZAÇÃO
    // ============================================
    serialize() {
        return {
            rivers: this.rivers.map(r => ({
                sourceIdx: r.sourceIdx,
                path: r.path
            })),
            enabled: this.isEnabled
        };
    }

    deserialize(data) {
        if (!data) return;
        
        this.setEnabled(data.enabled !== false);
        
        if (data.rivers && data.rivers.length > 0) {
            this.clearRivers();
            for (const riverData of data.rivers) {
                this.generateRiver(riverData.sourceIdx);
            }
        }
    }

    // ============================================
    // DESTRUIR
    // ============================================
    dispose() {
        this.clearRivers();
        
        for (const key in this.materials) {
            this.materials[key].dispose();
        }
        
        console.log('🗑️ RiverSystem disposed');
    }
}