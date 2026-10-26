import express from "express";
import { z } from "zod";

const CriarUsuario = z.object({
  nome: z.string().min(1),
  email: z.string().email(),
});
type Usuario = z.infer<typeof CriarUsuario> & { id: number };

class RepoUsuarios {
  private dados: Usuario[] = [];
  criar(d: z.infer<typeof CriarUsuario>): Usuario {
    const u = { ...d, id: this.dados.length + 1 };
    this.dados.push(u);
    return u;
  }
}
const repo = new RepoUsuarios(); // DI "na mão" (ou Nest)

export const app = express();
app.use(express.json());

app.post("/usuarios", (req, res) => {
  const r = CriarUsuario.safeParse(req.body);
  if (!r.success) return res.status(422).json(r.error.issues);
  res.status(201).json(repo.criar(r.data));
});
// app.listen(3000)   (dev: tsx watch ~ nodemon)
