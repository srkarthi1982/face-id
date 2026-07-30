declare module 'd3' {
  export interface ScalePoint<Domain extends string> {
    (value: Domain): number | undefined
    domain(values: Iterable<Domain>): ScalePoint<Domain>
    range(values: Iterable<number>): ScalePoint<Domain>
    padding(value: number): ScalePoint<Domain>
  }
  export interface ScaleLinear {
    (value: number): number
    domain(values: Iterable<number>): ScaleLinear
    range(values: Iterable<number>): ScaleLinear
    nice(): ScaleLinear
    ticks(count?: number): number[]
  }
  export interface LineGenerator<Datum> {
    (data: Iterable<Datum>): string | null
    x(accessor: (datum: Datum) => number): LineGenerator<Datum>
    y(accessor: (datum: Datum) => number): LineGenerator<Datum>
  }
  export function scalePoint<Domain extends string = string>(): ScalePoint<Domain>
  export function scaleLinear(): ScaleLinear
  export function max<Datum>(values: Iterable<Datum>, accessor: (datum: Datum) => number): number | undefined
  export function line<Datum>(): LineGenerator<Datum>
}
