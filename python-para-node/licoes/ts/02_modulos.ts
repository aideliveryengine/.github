// precos.ts: em Node o "módulo" é o arquivo, e só sai o que tem export.
export const IMPOSTO = 0.1;

export function comImposto(valor: number): number {
  return arredondar(valor * (1 + IMPOSTO));
}

// Sem export = privado de verdade: ninguém de fora acessa.
function arredondar(valor: number): number {
  return Math.round(valor * 100) / 100;
}

// Outro arquivo: import { comImposto } from "./precos.js";

// "Rodando direto, não importado?"
if (import.meta.url === `file://${process.argv[1]}`) {
  console.log(comImposto(100));
}
