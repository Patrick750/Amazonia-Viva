// Almacenamiento local de recorridos GPS en IndexedDB.
// Los puntos se guardan aquí antes de enviarse, así sobreviven a una pérdida de conexión
// o a cerrar la aplicación. Cada punto lleva `sincronizado` (0 pendiente, 1 enviado).
const NOMBRE_BD = 'amazonia-recorridos'
const VERSION_BD = 1

let conexion = null

const abrirBD = () => {
    if (conexion) return conexion
    conexion = new Promise((resolver, rechazar) => {
        const peticion = indexedDB.open(NOMBRE_BD, VERSION_BD)
        peticion.onupgradeneeded = () => {
            const bd = peticion.result
            bd.createObjectStore('recorridos', { keyPath: 'id_cliente' })
            const puntos = bd.createObjectStore('puntos', { keyPath: ['id_cliente', 'secuencia'] })
            puntos.createIndex('por_recorrido', 'id_cliente')
        }
        peticion.onsuccess = () => resolver(peticion.result)
        peticion.onerror = () => {
            conexion = null
            rechazar(peticion.error)
        }
    })
    return conexion
}

const ejecutar = async (almacenes, modo, operacion) => {
    const bd = await abrirBD()
    return new Promise((resolver, rechazar) => {
        const transaccion = bd.transaction(almacenes, modo)
        let resultado
        transaccion.oncomplete = () => resolver(resultado)
        transaccion.onerror = () => rechazar(transaccion.error)
        transaccion.onabort = () => rechazar(transaccion.error)
        resultado = operacion(transaccion)
    })
}

const pedir = (peticion) => new Promise((resolver, rechazar) => {
    peticion.onsuccess = () => resolver(peticion.result)
    peticion.onerror = () => rechazar(peticion.error)
})

export const guardarRecorrido = (recorrido) =>
    ejecutar('recorridos', 'readwrite', (t) => { t.objectStore('recorridos').put(recorrido) })

export const actualizarRecorrido = async (id, cambios) => {
    const bd = await abrirBD()
    const actual = await pedir(bd.transaction('recorridos').objectStore('recorridos').get(id))
    if (!actual) return null
    const nuevo = { ...actual, ...cambios }
    await guardarRecorrido(nuevo)
    return nuevo
}

export const obtenerRecorrido = async (id) => {
    const bd = await abrirBD()
    return pedir(bd.transaction('recorridos').objectStore('recorridos').get(id))
}

export const listarRecorridos = async () => {
    const bd = await abrirBD()
    return pedir(bd.transaction('recorridos').objectStore('recorridos').getAll())
}

export const guardarPunto = (punto) =>
    ejecutar('puntos', 'readwrite', (t) => { t.objectStore('puntos').put({ ...punto, sincronizado: 0 }) })

export const puntosDelRecorrido = async (id) => {
    const bd = await abrirBD()
    return pedir(bd.transaction('puntos').objectStore('puntos').index('por_recorrido').getAll(id))
}

export const puntosPendientes = async (id, limite = 200) => {
    const todos = await puntosDelRecorrido(id)
    return todos.filter(punto => !punto.sincronizado).sort((a, b) => a.secuencia - b.secuencia).slice(0, limite)
}

export const marcarSincronizados = (id, secuencias) =>
    ejecutar('puntos', 'readwrite', (t) => {
        const almacen = t.objectStore('puntos')
        secuencias.forEach((secuencia) => {
            const lectura = almacen.get([id, secuencia])
            lectura.onsuccess = () => {
                if (lectura.result) almacen.put({ ...lectura.result, sincronizado: 1 })
            }
        })
    })

export const contarPuntos = async (id) => {
    const puntos = await puntosDelRecorrido(id)
    return { total: puntos.length, pendientes: puntos.filter(punto => !punto.sincronizado).length }
}

export const eliminarRecorrido = (id) =>
    ejecutar(['recorridos', 'puntos'], 'readwrite', (t) => {
        t.objectStore('recorridos').delete(id)
        const indice = t.objectStore('puntos').index('por_recorrido')
        const cursor = indice.openKeyCursor(IDBKeyRange.only(id))
        cursor.onsuccess = () => {
            const actual = cursor.result
            if (actual) {
                t.objectStore('puntos').delete(actual.primaryKey)
                actual.continue()
            }
        }
    })
