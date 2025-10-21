// COMANDO PARA INSTALAR DEPENDÊNCIAS:
// npm install lucide-react dompurify
// npm install -D @types/dompurify

import { useEffect, useState } from "react";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardFooter,
} from "./components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "./components/ui/tabs";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationPrevious,
  PaginationNext,
  PaginationEllipsis,
} from "./components/ui/pagination";
import { Badge } from "./components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "./components/ui/dialog";
import { Skeleton } from "./components/ui/skeleton";

// Ícones
import {
  Search,
  X,
  Newspaper,
  CalendarDays,
  Tags,
  ExternalLink,
} from "lucide-react";

// Biblioteca de Segurança
import DOMPurify from "dompurify";

// Importações de assets (como no seu original)
import veja from "./public/assets/veja.jpeg";
import metropoles from "./public/assets/metropoles.jpeg";
import r7 from "./public/assets/r7.png";
import uol from "./public/assets/uol.png";
import maisgoias from "./public/assets/maisgoias.jpeg";
import aliadosbrasil from "./public/assets/aliadosbrasil.jpeg";
import ig from "./public/assets/IG.png";
import folha from "./public/assets/folha.jpeg";
import { DialogDescription, DialogTrigger } from "@radix-ui/react-dialog";

const API_URL = "http://localhost:8000";

const portalIcons: Record<string, string> = {
  metropoles_com: metropoles,
  veja_abril_com_br: veja,
  r7_com: r7,
  uol_com_br: uol,
  maisgoias_com_br: maisgoias,
  aliadosbrasiloficial_com_br: aliadosbrasil,
  ig_com_br: ig,
  folha_uol_com_br: folha,
};

// Função utilitária (como no seu original)
function formatarNomePortal(portal: string) {
  const nome = portal.replace(/_/g, ".").toLowerCase();
  return nome.charAt(0).toUpperCase() + nome.slice(1);
}

const Home = () => {
  const [portais, setPortais] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState("");
  const [portalSelecionado, setPortalSelecionado] = useState<string | null>(
    null
  );
  const [busca, setBusca] = useState("");
  const [noticias, setNoticias] = useState<any[]>([]);
  const [todasAsNoticiasDoPortal, setTodasAsNoticiasDoPortal] = useState<any[]>(
    []
  );
  const [carregandoNoticias, setCarregandoNoticias] = useState(false);
  const [erroNoticias, setErroNoticias] = useState("");
  const [pagina, setPagina] = useState(1);
  const noticiasPorPagina = 10;
  const [noticiaSelecionada, setNoticiaSelecionada] = useState<any | null>(
    null
  );
  const [dialogAberto, setDialogAberto] = useState(false);
  const [noticiasPorPortal, setNoticiasPorPortal] = useState<
    Record<string, number>
  >({});
  const [topTags, setTopTags] = useState<string[]>([]);

  useEffect(() => {
    fetch(`${API_URL}/portais`)
      .then((res) => res.json())
      .then(setPortais)
      .catch(() => setErro("Erro ao buscar portais"))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    setPagina(1);
  }, [portalSelecionado, busca]);

  useEffect(() => {
    if (!portalSelecionado) return;

    setCarregandoNoticias(true);
    setErroNoticias("");

    if (!busca.trim()) {
      // Busca todas as notícias do portal
      fetch(`${API_URL}/noticias/${portalSelecionado}`)
        .then((res) => res.json())
        .then((data) => {
          setNoticias(data);
          setTodasAsNoticiasDoPortal(data); // Armazena todas para as tags
        })
        .catch(() => setErroNoticias("Erro ao buscar notícias"))
        .finally(() => setCarregandoNoticias(false));
    } else {
      // Busca com termo de pesquisa
      const url = `${API_URL}/noticias/${portalSelecionado}/search?q=${encodeURIComponent(
        busca
      )}`;
      fetch(url)
        .then((res) => res.json())
        .then(setNoticias) // Atualiza 'noticias' com os resultados da busca
        .catch(() => setErroNoticias("Erro ao buscar notícias"))
        .finally(() => setCarregandoNoticias(false));

      // Nota: As 'topTags' não são recalculadas na busca,
      // elas permanecem as do portal como um todo. Isso é o comportamento esperado.
    }
  }, [portalSelecionado, busca]);

  // Calcula as Top Tags apenas quando 'todasAsNoticiasDoPortal' muda
  useEffect(() => {
    if (todasAsNoticiasDoPortal.length > 0) {
      const allTags = todasAsNoticiasDoPortal.flatMap(
        (noticia) => noticia.tags || []
      );
      const tagCounts = allTags.reduce((acc, tag) => {
        acc[tag] = (acc[tag] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);
      const sortedTags = Object.keys(tagCounts).sort(
        (a, b) => tagCounts[b] - tagCounts[a]
      );
      setTopTags(sortedTags.slice(0, 30));
    } else {
      setTopTags([]);
    }
  }, [todasAsNoticiasDoPortal]);

  const totalPaginas = Math.ceil(noticias.length / noticiasPorPagina);
  const inicio = (pagina - 1) * noticiasPorPagina;
  const fim = inicio + noticiasPorPagina;
  const noticiasPaginadas = noticias.slice(inicio, fim);

  useEffect(() => {
    const buscarContagemNoticias = async () => {
      const contagem: Record<string, number> = {};
      for (const portal of portais) {
        try {
          const response = await fetch(`${API_URL}/noticias/${portal}`);
          const noticiasPortal = await response.json();
          contagem[portal] = noticiasPortal.length;
        } catch (error) {
          contagem[portal] = 0;
        }
      }
      setNoticiasPorPortal(contagem);
    };

    if (portais.length > 0) {
      buscarContagemNoticias();
    }
  }, [portais]);

  const handleTagClick = (tag: string) => {
    // Se a tag clicada já está na busca, limpa a busca. Senão, define a busca.
    if (busca === tag) {
      setBusca("");
    } else {
      setBusca(tag);
    }
  };

  const handlePortalChange = (novoPortal: string) => {
    setPortalSelecionado(novoPortal);
    setBusca(""); // Limpa a busca ao trocar de portal
  };

  // --- LÓGICA DE PAGINAÇÃO MELHORADA ---
  const getPaginationRange = () => {
    const siblingCount = 1;
    const totalPageNumbers = siblingCount + 5; // siblingCount + first + last + current + 2*ellipsis

    if (totalPageNumbers >= totalPaginas) {
      return Array.from({ length: totalPaginas }, (_, i) => i + 1);
    }

    const leftSiblingIndex = Math.max(pagina - siblingCount, 1);
    const rightSiblingIndex = Math.min(pagina + siblingCount, totalPaginas);

    const shouldShowLeftDots = leftSiblingIndex > 2;
    const shouldShowRightDots = rightSiblingIndex < totalPaginas - 2;

    const firstPageIndex = 1;
    const lastPageIndex = totalPaginas;

    if (!shouldShowLeftDots && shouldShowRightDots) {
      let leftItemCount = 3 + 2 * siblingCount;
      let leftRange = Array.from({ length: leftItemCount }, (_, i) => i + 1);
      return [...leftRange, "...", totalPaginas];
    }

    if (shouldShowLeftDots && !shouldShowRightDots) {
      let rightItemCount = 3 + 2 * siblingCount;
      let rightRange = Array.from(
        { length: rightItemCount },
        (_, i) => totalPaginas - i
      ).reverse();
      return [firstPageIndex, "...", ...rightRange];
    }

    if (shouldShowLeftDots && shouldShowRightDots) {
      let middleRange = Array.from(
        { length: rightSiblingIndex - leftSiblingIndex + 1 },
        (_, i) => leftSiblingIndex + i
      );
      return [firstPageIndex, "...", ...middleRange, "...", lastPageIndex];
    }
    return []; // Fallback
  };
  const pageNumbers = getPaginationRange();
  // --- FIM DA LÓGICA DE PAGINAÇÃO ---

  // ESTADO DE LOADING
  if (loading)
    return (
      <div className="max-w-5xl mx-auto p-8">
        {" "}
        {/* Aumentado max-w-2xl para 5xl */}
        <h1 className="text-2xl font-bold mb-4">
          Selecione um portal de notícias
        </h1>
        <div className="space-y-6">
          <div className="mx-auto flex w-full max-w-4xl bg-gray-200 rounded-md mb-6">
            {Array.from({ length: 4 }, (_, idx) => (
              <div
                key={idx}
                className="group flex-1 flex items-center justify-center gap-2 p-3 text-xs"
              >
                <Skeleton className="h-5 w-5 rounded-full" />
                <Skeleton className="h-4 w-16" />
                <Skeleton className="h-5 w-8 rounded-md" />
              </div>
            ))}
          </div>
          <div className="space-y-4">
            <Skeleton className="h-4 w-48" />
            <Skeleton className="h-10 w-full" />
            <div className="grid gap-4">
              {Array.from({ length: 3 }, (_, idx) => (
                <Card key={idx}>
                  <CardHeader>
                    <Skeleton className="h-6 w-3/4" />
                  </CardHeader>
                  <CardContent>
                    <Skeleton className="h-4 w-full mb-2" />
                    <Skeleton className="h-4 w-2/3" />
                  </CardContent>
                  <CardFooter>
                    <Skeleton className="h-4 w-20" />
                  </CardFooter>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </div>
    );

  // ESTADO DE ERRO
  if (erro) return <div className="p-8 text-red-500">{erro}</div>;

  // ESTADO PRINCIPAL (CARREGADO)
  return (
    <div className="max-w-5xl mx-auto p-8">
      <h1 className="text-2xl font-bold mb-4">
        Selecione um portal de notícias
      </h1>
      {portais.length > 0 && (
        <Tabs
          value={portalSelecionado ?? undefined}
          onValueChange={handlePortalChange}
          className="w-full"
        >
          <TabsList className="mx-auto flex w-full max-w-4xl bg-transparent mb-6 h-auto flex-wrap">
            {portais.map((portal) => {
              return (
                <TabsTrigger
                  key={portal}
                  value={portal}
                  className="group data-[state=active]:bg-muted flex-1 flex-col p-3 text-xs data-[state=active]:shadow-none min-w-fit gap-2 items-center"
                >
                  {portalIcons[portal] && (
                    <img
                      src={portalIcons[portal]}
                      alt={`${formatarNomePortal(portal)} logo`}
                      className="h-10 w-10 object-contain rounded-sm"
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = "none";
                      }}
                    />
                  )}
                  <span>{formatarNomePortal(portal)}</span>
                  <Badge className="min-w-5 px-1 transition-opacity group-data-[state=inactive]:opacity-50">
                    {noticiasPorPortal[portal] ?? (
                      <Skeleton className="w-3 h-3" />
                    )}
                  </Badge>
                </TabsTrigger>
              );
            })}
          </TabsList>

          {/* --- IDEIA: ESTADO DE BOAS-VINDAS --- */}
          {!portalSelecionado && (
            <div className="text-center p-16 border-2 border-dashed rounded-lg mt-6 bg-slate-50">
              <Newspaper className="w-16 h-16 mx-auto mt-4 text-zinc-400 mb-6" />
              <h2 className="text-2xl font-semibold text-zinc-700 mb-2">
                Bem-vindo ao seu Agregador de Notícias
              </h2>
              <p className="text-lg text-zinc-500">
                Selecione um portal acima para começar a ler as últimas
                notícias.
              </p>
            </div>
          )}

          {/* Mostra o conteúdo apenas se um portal estiver selecionado */}
          {portalSelecionado &&
            portais.map((portal) => (
              <TabsContent key={portal} value={portal}>
                <div className="mb-2 font-semibold">
                  Portal selecionado:{" "}
                  <span className="text-blue-600">
                    {formatarNomePortal(portal)}
                  </span>
                </div>
                <div className="flex flex-col md:flex-row gap-8 mt-4">
                  <aside className="w-full md:w-1/4 lg:w-1/5">
                    <h3 className="font-semibold mb-4 text-lg">
                      Tags Populares
                    </h3>
                    {carregandoNoticias ? (
                      <div className="flex flex-wrap gap-2">
                        {Array.from({ length: 10 }, (_, idx) => (
                          <Skeleton
                            key={idx}
                            className="h-6 w-16 rounded-full"
                          />
                        ))}
                      </div>
                    ) : topTags.length > 0 ? (
                      <div className="flex flex-wrap gap-2">
                        {topTags.map((tag, idx) => (
                          <Badge
                            key={idx}
                            // --- IDEIA: FEEDBACK DE TAG ATIVA ---
                            variant={busca === tag ? "default" : "secondary"}
                            className="cursor-pointer hover:bg-primary/20 transition-colors"
                            onClick={() => handleTagClick(tag)}
                          >
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-zinc-500">
                        Nenhuma tag encontrada para este portal.
                      </p>
                    )}
                  </aside>

                  <main className="flex-1">
                    {/* --- IDEIA: INPUT DE BUSCA MELHORADO --- */}
                    <div className="relative mb-4">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400" />
                      <Input
                        placeholder="Buscar notícias ou clique em uma tag..."
                        value={busca}
                        onChange={(e) => setBusca(e.target.value)}
                        className="pl-10 pr-10" // Padding para os ícones
                      />
                      {busca.length > 0 && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="absolute right-1 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full"
                          onClick={() => setBusca("")}
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      )}
                    </div>

                    {carregandoNoticias ? (
                      <div className="grid gap-4">
                        {Array.from({ length: 5 }, (_, idx) => (
                          <Card key={idx}>
                            <CardHeader>
                              <Skeleton className="h-6 w-3/4" />
                            </CardHeader>
                            <CardContent>
                              <Skeleton className="h-4 w-full mb-2" />
                              <Skeleton className="h-4 w-2/3" />
                            </CardContent>
                            <CardFooter>
                              <Skeleton className="h-4 w-20" />
                            </CardFooter>
                          </Card>
                        ))}
                      </div>
                    ) : erroNoticias ? (
                      <div className="text-red-500">{erroNoticias}</div>
                    ) : noticiasPaginadas.length === 0 ? (
                      <div>
                        Nenhuma notícia encontrada
                        {busca.trim() && ` para "${busca}"`}.
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {noticiasPaginadas.map((noticia, idx) => (
                          <Dialog
                            key={idx}
                            open={
                              dialogAberto && noticiaSelecionada === noticia
                            }
                            onOpenChange={(open) => {
                              setDialogAberto(open);
                              if (!open) setNoticiaSelecionada(null);
                            }}
                          >
                            <DialogTrigger asChild>
                              {/* --- IDEIA: CARD DE NOTÍCIA MELHORADO --- */}
                              <Card
                                className="cursor-pointer hover:shadow-lg transition-shadow flex flex-col justify-between min-h-[200px]"
                                onClick={() => {
                                  setNoticiaSelecionada(noticia);
                                  setDialogAberto(true);
                                }}
                              >
                                <div>
                                  <CardHeader>
                                    <CardTitle className="text-lg">
                                      {noticia.title}
                                    </CardTitle>
                                  </CardHeader>
                                  {noticia.description && (
                                    <CardContent>
                                      <p className="text-zinc-700 text-sm line-clamp-3 leading-relaxed">
                                        {noticia.description}
                                      </p>
                                    </CardContent>
                                  )}
                                </div>
                                <CardFooter className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 pt-4">
                                  {noticia.date ? (
                                    <span className="text-xs text-zinc-500">
                                      {new Date(
                                        noticia.date
                                      ).toLocaleDateString("pt-BR", {
                                        day: "2-digit",
                                        month: "long",
                                        year: "numeric",
                                      })}
                                    </span>
                                  ) : (
                                    <div />
                                  )}{" "}
                                  {/* Div vazia para manter o alinhamento */}
                                  {noticia.tags && noticia.tags.length > 0 && (
                                    <div className="flex flex-wrap gap-1 justify-end max-w-xs">
                                      {noticia.tags
                                        .slice(0, 2)
                                        .map((tag: string, tagIdx: number) => (
                                          <Badge
                                            key={tagIdx}
                                            variant="secondary"
                                            className="text-xs"
                                          >
                                            {tag}
                                          </Badge>
                                        ))}
                                      {noticia.tags.length > 2 && (
                                        <Badge
                                          variant="outline"
                                          className="text-xs"
                                        >
                                          +{noticia.tags.length - 2}
                                        </Badge>
                                      )}
                                    </div>
                                  )}
                                </CardFooter>
                              </Card>
                            </DialogTrigger>
                            {/* --- IDEIA: MODAL (DIALOG) MELHORADA --- */}
                            <DialogContent>
                              {" "}
                              {/* <-- Sem classes extras aqui! O default do novo dialog.tsx cuida disso. */}
                              <DialogHeader>
                                <DialogTitle>{noticia.title}</DialogTitle>
                                {/* Eu movi os metadados para dentro da Descrição, fica mais semântico */}
                                <DialogDescription asChild>
                                  <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm pt-2">
                                    {noticia.date && (
                                      <div className="flex items-center gap-2">
                                        <CalendarDays className="w-4 h-4" />
                                        <span>
                                          {new Date(
                                            noticia.date
                                          ).toLocaleDateString("pt-BR", {
                                            dateStyle: "long",
                                          })}
                                        </span>
                                      </div>
                                    )}
                                    {noticia.tags &&
                                      noticia.tags.length > 0 && (
                                        <div className="flex items-center gap-2">
                                          <Tags className="w-4 h-4" />
                                          <span className="font-medium">
                                            Tags:
                                          </span>
                                          <span className="text-zinc-800">
                                            {noticia.tags.join(", ")}
                                          </span>
                                        </div>
                                      )}
                                  </div>
                                </DialogDescription>
                              </DialogHeader>
                              {/* ESTA É A PARTE MAIS IMPORTANTE: O DIV COM SCROLL */}
                              <div className="p-6 overflow-y-auto">
                                <div className="space-y-6">
                                  {noticia.description && (
                                    <p className="text-lg text-zinc-800 italic leading-relaxed border-l-4 pl-4">
                                      {noticia.description}
                                    </p>
                                  )}

                                  {noticia.body && (
                                    <div>
                                      <h4 className="font-semibold mb-3 text-lg">
                                        Conteúdo Completo
                                      </h4>
                                      <div
                                        className="prose prose-zinc max-w-none prose-sm sm:prose-base text-justify whitespace-pre-line"
                                    dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(noticia.body) }}
                                      />
                                    </div>
                                  )}
                                </div>
                              </div>
                              {noticia.url && (
                                <DialogFooter>
                                  <Button asChild variant="default">
                                    <a
                                      href={noticia.url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                    >
                                      Ver Notícia Original
                                      <ExternalLink className="w-4 h-4 ml-2" />
                                    </a>
                                  </Button>
                                </DialogFooter>
                              )}
                            </DialogContent>
                          </Dialog>
                        ))}
                      </div>
                    )}
                    {/* --- IDEIA: PAGINAÇÃO COMPLETA --- */}
                    {totalPaginas > 1 && (
                      <div className="flex items-center justify-between gap-3 mt-6">
                        <p
                          className="text-muted-foreground grow text-sm"
                          aria-live="polite"
                        >
                          Página{" "}
                          <span className="text-foreground">{pagina}</span> de{" "}
                          <span className="text-foreground">
                            {totalPaginas}
                          </span>
                        </p>
                        <Pagination className="w-auto">
                          <PaginationContent>
                            <PaginationItem>
                              <PaginationPrevious
                                href="#"
                                onClick={(e) => {
                                  e.preventDefault();
                                  setPagina((p) => Math.max(1, p - 1));
                                }}
                                className={
                                  pagina === 1
                                    ? "pointer-events-none opacity-50"
                                    : undefined
                                }
                              />
                            </PaginationItem>
                            {pageNumbers.map((page, idx) => (
                              <PaginationItem key={idx}>
                                {typeof page === "string" ? (
                                  <PaginationEllipsis />
                                ) : (
                                  <PaginationLink
                                    href="#"
                                    onClick={(e) => {
                                      e.preventDefault();
                                      setPagina(page);
                                    }}
                                    isActive={pagina === page}
                                  >
                                    {page}
                                  </PaginationLink>
                                )}
                              </PaginationItem>
                            ))}
                            <PaginationItem>
                              <PaginationNext
                                href="#"
                                onClick={(e) => {
                                  e.preventDefault();
                                  setPagina((p) =>
                                    Math.min(totalPaginas, p + 1)
                                  );
                                }}
                                className={
                                  pagina === totalPaginas
                                    ? "pointer-events-none opacity-50"
                                    : undefined
                                }
                              />
                            </PaginationItem>
                          </PaginationContent>
                        </Pagination>
                      </div>
                    )}
                  </main>
                </div>
              </TabsContent>
            ))}
        </Tabs>
      )}
    </div>
  );
};

export default Home;
