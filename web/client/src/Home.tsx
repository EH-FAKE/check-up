import { useEffect, useState } from "react";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "./components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "./components/ui/tabs";
import { Pagination, PaginationContent, PaginationItem } from "./components/ui/pagination";
import { Badge } from "./components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "./components/ui/dialog";
import { Skeleton } from "./components/ui/skeleton";

import veja from './public/assets/veja.jpeg';
import metropoles from './public/assets/metropoles.jpeg'
import r7 from './public/assets/r7.png'
import  uol from './public/assets/uol.png'
import maisgoias from './public/assets/maisgoias.jpeg'
import  aliadosbrasil from './public/assets/aliadosbrasil.jpeg'
import  ig from './public/assets/IG.png'
import  folha from './public/assets/folha.jpeg'
const API_URL = "http://localhost:8000"

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
// Função utilitária para formatar o nome do portal
function formatarNomePortal(portal: string) {
	const nome = portal.replace(/_/g, ".").toLowerCase();
	return nome.charAt(0).toUpperCase() + nome.slice(1);
}

const Home = () => {
    const [portais, setPortais] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);
    const [erro, setErro] = useState("");
    const [portalSelecionado, setPortalSelecionado] = useState<string | null>(
        null,
    );
    const [busca, setBusca] = useState("");
    const [noticias, setNoticias] = useState<any[]>([]);
    const [carregandoNoticias, setCarregandoNoticias] = useState(false);
    const [erroNoticias, setErroNoticias] = useState("");
    const [pagina, setPagina] = useState(1);
    const noticiasPorPagina = 10;
    const [noticiaSelecionada, setNoticiaSelecionada] = useState<any | null>(null);
    const [dialogAberto, setDialogAberto] = useState(false);
    const [noticiasPorPortal, setNoticiasPorPortal] = useState<Record<string, number>>({});

    useEffect(() => {
        fetch(`${API_URL}/portais`)
            .then((res) => res.json())
            .then(setPortais)
            .catch(() => setErro("Erro ao buscar portais"))
            .finally(() => setLoading(false));
    }, []);

    useEffect(() => {
        setPagina(1); // Sempre volta para a primeira página ao trocar portal ou busca
    }, [portalSelecionado, busca]);

    useEffect(() => {
        if (!portalSelecionado) return;
        setCarregandoNoticias(true);
        setErroNoticias("");
        const url = busca.trim()
            ? `${API_URL}/noticias/${portalSelecionado}/search?q=${encodeURIComponent(busca)}`
            : `${API_URL}/noticias/${portalSelecionado}`;
        fetch(url)
            .then((res) => res.json())
            .then(setNoticias)
            .catch(() => setErroNoticias("Erro ao buscar notícias"))
            .finally(() => setCarregandoNoticias(false));
    }, [portalSelecionado, busca]);

    // Paginação no frontend
    const totalPaginas = Math.ceil(noticias.length / noticiasPorPagina);
    const inicio = (pagina - 1) * noticiasPorPagina;
    const fim = inicio + noticiasPorPagina;
    const noticiasPaginadas = noticias.slice(inicio, fim);

    useEffect(() => {
        // Buscar contagem de notícias para cada portal
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

    if (loading) return (
        <div className="max-w-2xl mx-auto p-8">
            <h1 className="text-2xl font-bold mb-4">
                Selecione um portal de notícias
            </h1>
            <div className="space-y-6">
                {/* Skeleton das Tabs  */}
                <div className="mx-auto flex w-full max-w-4xl bg-gray-200 rounded-md mb-6">
                    {Array.from({ length: 4 }, (_, idx) => (
                        <div key={idx} className="group flex-1 flex items-center justify-center gap-2 p-3 text-xs">
                            <Skeleton className="h-5 w-5 rounded-full" />
                            <Skeleton className="h-4 w-16" />
                            <Skeleton className="h-5 w-8 rounded-md" />
                        </div>
                    ))}
                </div>
                {/* Skeleton do conteúdo */}
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
    if (erro) return <div className="p-8 text-red-500">{erro}</div>;

    return (
        <div className="max-w-2xl mx-auto p-8">
            <h1 className="text-2xl font-bold mb-4">
                Selecione um portal de notícias
            </h1>
            {portais.length > 0 && (
                <Tabs value={portalSelecionado ?? undefined} onValueChange={setPortalSelecionado} className="w-full">
                    <TabsList className="mx-auto flex w-full max-w-4xl bg-transparent mb-6 h-auto ">
                        {portais.map((portal) => {
                            //console.log(`[Debug] Portal: "${portal}", Caminho do Ícone: "${portalIcons[portal]}"`);
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
                                            onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                                        />
                                    )}
                                    <span>{formatarNomePortal(portal)}</span>
                                    <Badge className="min-w-5 px-1 transition-opacity group-data-[state=inactive]:opacity-50">
                                        {noticiasPorPortal[portal] || 0}
                                    </Badge>
                                  
                                </TabsTrigger>
                            );
                        })}
                    </TabsList>
                    {portais.map((portal) => (
                        <TabsContent key={portal} value={portal}>
                            <div className="mb-2 font-semibold">
                                Portal selecionado: <span className="text-blue-600">{formatarNomePortal(portal)}</span>
                            </div>
                            <div className="mt-4">
                                <div className="flex gap-2 mb-4">
                                    <Input
                                        placeholder="Buscar notícias..."
                                        value={busca}
                                        onChange={(e) => setBusca(e.target.value)}
                                    />
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
                                    <div>Nenhuma notícia encontrada.</div>
                                ) : (
                                    <div className="grid gap-4">
                                        {noticiasPaginadas.map((noticia, idx) => (
                                            <Dialog key={idx} open={dialogAberto && noticiaSelecionada === noticia} onOpenChange={(open) => {
                                                setDialogAberto(open);
                                                if (!open) setNoticiaSelecionada(null);
                                            }}>
                                                <DialogTrigger asChild>
                                                    <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => {
                                                        setNoticiaSelecionada(noticia);
                                                        setDialogAberto(true);
                                                    }}>
                                                        <CardHeader>
                                                            <CardTitle>{noticia.title}</CardTitle>
                                                        </CardHeader>
                                                        <CardContent>
                                                            {noticia.description && (
                                                                <div className="text-zinc-700 text-sm line-clamp-2 mb-2 whitespace-pre-line leading-relaxed">{noticia.description}</div>
                                                            )}
                                                        </CardContent>
                                                        {noticia.link && (
                                                            <CardFooter>
                                                                <a href={noticia.link} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline text-sm">Ler mais</a>
                                                            </CardFooter>
                                                        )}
                                                    </Card>
                                                </DialogTrigger>
                                                <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                                                    <DialogHeader>
                                                        <DialogTitle>{noticia.title}</DialogTitle>
                                                    </DialogHeader>
                                                    <div className="space-y-4">
                                                        {noticia.description && (
                                                            <div>
                                                                <h4 className="font-semibold mb-2">Descrição</h4>
                                                                <p className="text-zinc-700">{noticia.description}</p>
                                                            </div>
                                                        )}
                                                        {noticia.body && (
                                                            <div>
                                                                <h4 className="font-semibold mb-2">Conteúdo</h4>
                                                                <div className="text-zinc-700 prose prose-sm max-w-none" dangerouslySetInnerHTML={{ __html: noticia.body }} />
                                                            </div>
                                                        )}
                                                        {noticia.tags && noticia.tags.length > 0 && (
                                                            <div>
                                                                <h4 className="font-semibold mb-2">Tags</h4>
                                                                <div className="flex flex-wrap gap-2">
                                                                    {noticia.tags.map((tag: string, tagIdx: number) => (
                                                                        <Badge key={tagIdx} variant="secondary">{tag}</Badge>
                                                                    ))}
                                                                </div>
                                                            </div>
                                                        )}
                                                        {noticia.date && (
                                                            <div>
                                                                <h4 className="font-semibold mb-2">Data</h4>
                                                                <p className="text-zinc-600">{new Date(noticia.date).toLocaleDateString('pt-BR')}</p>
                                                            </div>
                                                        )}
                                                    </div>
                                                    {noticia.url && (
                                                        <div className="pt-4 border-t flex justify-end">
                                                            <Button asChild variant="link" className="px-0 text-blue-600 underline text-base">
                                                                <a href={noticia.url} target="_blank" rel="noopener noreferrer">
                                                                    Ver notícia original
                                                                </a>
                                                            </Button>
                                                        </div>
                                                    )}
                                                </DialogContent>
                                            </Dialog>
                                        ))}
                                    </div>
                                )}
                                {totalPaginas > 1 && (
                                    <div className="flex items-center justify-between gap-3 mt-6">
                                        <p className="text-muted-foreground grow text-sm" aria-live="polite">
                                            Página <span className="text-foreground">{pagina}</span> de{" "}
                                            <span className="text-foreground">{totalPaginas}</span>
                                        </p>
                                        <Pagination className="w-auto">
                                            <PaginationContent className="gap-3">
                                                <PaginationItem>
                                                    <Button
                                                        variant="outline"
                                                        className="aria-disabled:pointer-events-none aria-disabled:opacity-50"
                                                        aria-disabled={pagina === 1 ? true : undefined}
                                                        onClick={() => setPagina((p) => Math.max(1, p - 1))}
                                                        disabled={pagina === 1}
                                                    >
                                                        Anterior
                                                    </Button>
                                                </PaginationItem>
                                                <PaginationItem>
                                                    <Button
                                                        variant="outline"
                                                        className="aria-disabled:pointer-events-none aria-disabled:opacity-50"
                                                        aria-disabled={pagina === totalPaginas ? true : undefined}
                                                        onClick={() => setPagina((p) => Math.min(totalPaginas, p + 1))}
                                                        disabled={pagina === totalPaginas}
                                                    >
                                                        Próxima
                                                    </Button>
                                                </PaginationItem>
                                            </PaginationContent>
                                        </Pagination>
                                    </div>
                                )}
                            </div>
                        </TabsContent>
                    ))}
                </Tabs>
            )}
        </div>
    );
};

export default Home;
