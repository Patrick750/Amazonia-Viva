// Cola de evidencias fotográficas pendientes de subir, guardada en IndexedDB.
// Las fotos se guardan aquí antes de enviarse, así que sobreviven a recargar la página o cerrar el navegador
// y la subida puede continuar. Cada registro: { id, usuario, detalle, archivo (File), creado }.
const NOMBRE_BD = 'amazonia-evidencias'
const ALMACEN = 'pendientes'

let conexion = null

const abrirBD = () => {
    if (conexion) return conexion
    conexion = new Promise((resolver, rechazar) => {
        const peticion = indexedDB.open(NOMBRE_BD, 1)
        peticion.onupgradeneeded = () => {
            const almacen = peticion.result.createObjectStore(ALMACEN, { keyPath: 'id' })
            almacen.createIndex('por_usuario', 'usuario')
        }
        peticion.onsuccess = () => resolver(peticion.result)
        peticion.onerror = () => {
            conexion = null
            rechazar(peticion.error)
        }
    })
    return conexion
}

const transaccion = async (modo, operacion) => {
    const bd = await abrirBD()
    return new Promise((resolver, rechazar) => {
        const t = bd.transaction(ALMACEN, modo)
        let resultado
        t.oncomplete = () => resolver(resultado)
        t.onerror = () => rechazar(t.error)
        t.onabort = () => rechazar(t.error)
        resultado = operacion(t.objectStore(ALMACEN))
    })
}

export const guardarPendientes = (registros) =>
    transaccion('readwrite', (almacen) => { registros.forEach(registro => almacen.put(registro)) })

export const eliminarPendientes = (ids) =>
    transaccion('readwrite', (almacen) => { ids.forEach(id => almacen.delete(id)) })

// Solo las de la cuenta indicada: otra persona que use el mismo navegador no debe retomar fotos ajenas.
export const listarPendientes = async (usuario) => {
    const bd = await abrirBD()
    return new Promise((resolver, rechazar) => {
        const peticion = bd.transaction(ALMACEN).objectStore(ALMACEN).index('por_usuario').getAll(usuario)
        peticion.onsuccess = () => resolver(peticion.result.sort((a, b) => a.creado - b.creado))
        peticion.onerror = () => rechazar(peticion.error)
    })
}
