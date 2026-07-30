// Polyfill for older browsers that don't support Object.hasOwn (ES2022)
if (!(Object as any).hasOwn) {
  ;(Object as any).hasOwn = function (obj: unknown, prop: string | symbol) {
    return Object.prototype.hasOwnProperty.call(obj, prop)
  }
}
