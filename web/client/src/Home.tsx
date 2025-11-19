// COMANDO PARA INSTALAR DEPENDÊNCIAS:
// npm install lucide-react dompurify
// npm install -D @types/dompurify

import { useEffect, useMemo, useState } from "react"; 
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "./components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "./components/ui/tabs";
import { 
    Pagination, 
    PaginationContent, 
    PaginationItem,
    PaginationLink,
    PaginationPrevious,
    PaginationNext,
    PaginationEllipsis
} from "./components/ui/pagination";
import { Badge } from "./components/ui/badge";
import { 
    Dialog, 
    DialogContent, 
    DialogHeader, 
    DialogTitle, 
    DialogFooter, 
    DialogTrigger,
    DialogDescription 
} from "./components/ui/dialog";
import { Skeleton } from "./components/ui/skeleton";
import { cn } from "@/lib/utils"; 
import { Search, X, Newspaper, CalendarDays, Tags, ExternalLink, Star, Frown, Clock, Link as LinkIcon, Check } from "lucide-react"; 

// Biblioteca de Segurança
import DOMPurify from 'dompurify';

// Importações de assets
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

function formatarNomePortal(portal: string) {
    const nome = portal.replace(/_/g, ".").toLowerCase();
    return nome.charAt(0).toUpperCase() + nome.slice(1);
}
function limparLixoVisual(html: string) {
    if (!html) return "";
    let linhas = html.split('\n');
    let modoExclusao = false; 

    const termosBanidos = [
        "FONTE/CRÉDITOS", "FONTE/CREDITOS",
        "CRÉDITOS (IMAGEM DE CAPA)", "CRÉDITOS:", "CREDITOS:", "FONTE:",
        ,"PUBLICIDADE","MAIS LIDAS" // Tags soltas
    ];

    // Filtra as linhas
    linhas = linhas.filter(linha => {
        const conteudo = linha.trim();
        const conteudoUpper = conteudo.toUpperCase();

        // 1. Verifica se a linha começa o bloco "LEIA TAMBÉM"
        if (conteudoUpper.includes("LEIA TAMBÉM") || conteudoUpper.includes("LEIA TAMBEM")) {
            modoExclusao = true; 
            return false; 
        }

        // 2. Se estivermos no modo de exclusão (logo após um LEIA TAMBÉM)
        if (modoExclusao) {
            if (conteudo.length < 150 && conteudo.length > 0) {
                return false; 
            } else if (conteudo.length >= 150) {
                modoExclusao = false; 
            }
        }

        return true;
    });

    return linhas.join('\n');
}
function calcularTempoLeitura(texto: string | undefined) {
    if (!texto) return "1 min";
    const palavras = texto.split(/\s+/).length;
    const minutos = Math.ceil(palavras / 200); 
    return `${minutos} min`;
}

const Home = () => {
    const [portais, setPortais] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);
    const [erro, setErro] = useState("");
    const [portalSelecionado, setPortalSelecionado] = useState<string | null>(null);
    const [noticias, setNoticias] = useState<any[]>([]);
    const [todasAsNoticiasDoPortal, setTodasAsNoticiasDoPortal] = useState<any[]>([]);
    const [carregandoNoticias, setCarregandoNoticias] = useState(false);
    const [erroNoticias, setErroNoticias] = useState("");
    const [noticiaSelecionada, setNoticiaSelecionada] = useState<any | null>(null);
    const [dialogAberto, setDialogAberto] = useState(false);
    const [noticiasPorPortal, setNoticiasPorPortal] = useState<Record<string, number>>({});
    const [tamanhoFonte, setTamanhoFonte] = useState("text-base"); 
    const [copiadoId, setCopiadoId] = useState<string | null>(null); // Para feedback visual

    // Estados para a seção de PORTAIS
    const [buscaPortal, setBuscaPortal] = useState("");
    const [paginaPortal, setPaginaPortal] = useState(1);
    const [topTagsPortal, setTopTagsPortal] = useState<string[]>([]);

    // Estados para a seção de FAVORITOS
    const [buscaFavoritos, setBuscaFavoritos] = useState("");
    const [paginaFavoritos, setPaginaFavoritos] = useState(1);
    const [topTagsFavoritos, setTopTagsFavoritos] = useState<string[]>([]);
    
    const noticiasPorPagina = 10;

    // --- LÓGICA DE FAVORITOS (Início) ---
    const [favoritos, setFavoritos] = useState<any[]>(() => {
        try {
            const saved = localStorage.getItem("favoritos");
            return saved ? JSON.parse(saved) : [];
        } catch (error) {
            console.error("Erro ao ler favoritos do localStorage", error);
            return [];
        }
    });

    useEffect(() => {
        localStorage.setItem("favoritos", JSON.stringify(favoritos));
    }, [favoritos]);

    const isNoticiaFavorita = (noticia: any) => {
        return favoritos.some(fav => fav.url === noticia.url); 
    };

    const handleToggleFavorito = (noticia: any) => {
        if (isNoticiaFavorita(noticia)) {
            setFavoritos(prev => prev.filter(fav => fav.url !== noticia.url));
        } else {
            setFavoritos(prev => [noticia, ...prev]); 
        }
    };

    const handleCopiarLink = (url: string, id: string) => {
        navigator.clipboard.writeText(url);
        setCopiadoId(id);
        setTimeout(() => setCopiadoId(null), 2000);
    }

    // --- LÓGICA DE FAVORITOS (Fim) ---


    useEffect(() => {
        fetch(`${API_URL}/portais`)
            .then((res) => res.json())
            .then(setPortais)
            .catch(() => setErro("Erro ao buscar portais"))
            .finally(() => setLoading(false));
    }, []);

    // Reseta paginação do PORTAL quando a busca ou portal muda
    useEffect(() => {
        setPaginaPortal(1); 
    }, [portalSelecionado, buscaPortal]);

    // Reseta paginação dos FAVORITOS quando a busca de favoritos muda
    useEffect(() => {
        setPaginaFavoritos(1);
    }, [buscaFavoritos]);

    // Busca notícias da API (para portais)
    useEffect(() => {
        if (!portalSelecionado || portalSelecionado === 'favoritos') {
            setNoticias([]);
            setTodasAsNoticiasDoPortal([]);
            return;
        }

        setCarregandoNoticias(true);
        setErroNoticias("");

        if (!buscaPortal.trim()) {
            fetch(`${API_URL}/noticias/${portalSelecionado}`)
                .then((res) => res.json())
                .then((data) => {
                    setNoticias(data);
                    setTodasAsNoticiasDoPortal(data);
                })
                .catch(() => setErroNoticias("Erro ao buscar notícias"))
                .finally(() => setCarregandoNoticias(false));
        } else {
            const url = `${API_URL}/noticias/${portalSelecionado}/search?q=${encodeURIComponent(buscaPortal)}`;
            fetch(url)
                .then((res) => res.json())
                .then(setNoticias)
                .catch(() => setErroNoticias("Erro ao buscar notícias"))
                .finally(() => setCarregandoNoticias(false));
        }
    }, [portalSelecionado, buscaPortal]);

    // Calcula as Top Tags do PORTAL
    useEffect(() => {
        if (todasAsNoticiasDoPortal.length > 0) {
            const allTags = todasAsNoticiasDoPortal.flatMap(noticia => noticia.tags || []);
            const tagCounts = allTags.reduce((acc, tag) => {
                acc[tag] = (acc[tag] || 0) + 1;
                return acc;
            }, {} as Record<string, number>);
            const sortedTags = Object.keys(tagCounts).sort((a, b) => tagCounts[b] - tagCounts[a]);
            setTopTagsPortal(sortedTags.slice(0, 30));
        } else {
            setTopTagsPortal([]);
        }
    }, [todasAsNoticiasDoPortal]);

    // Calcula as Top Tags dos FAVORITOS
    useEffect(() => {
        if (favoritos.length > 0) {
            const allTags = favoritos.flatMap(noticia => noticia.tags || []);
            const tagCounts = allTags.reduce((acc, tag) => {
                acc[tag] = (acc[tag] || 0) + 1;
                return acc;
            }, {} as Record<string, number>);
            const sortedTags = Object.keys(tagCounts).sort((a, b) => tagCounts[b] - tagCounts[a]);
            setTopTagsFavoritos(sortedTags.slice(0, 30));
        } else {
            setTopTagsFavoritos([]);
        }
    }, [favoritos]);


    // Paginação e dados para PORTAIS
    const totalPaginasPortal = Math.ceil(noticias.length / noticiasPorPagina);
    const inicioPortal = (paginaPortal - 1) * noticiasPorPagina;
    const fimPortal = inicioPortal + noticiasPorPagina;
    const noticiasPaginadasPortal = noticias.slice(inicioPortal, fimPortal);

    // Filtro e Paginação para FAVORITOS
    const favoritosFiltrados = useMemo(() => {
        if (!buscaFavoritos.trim()) {
            return favoritos;
        }
        const lowerBusca = buscaFavoritos.toLowerCase();
        return favoritos.filter(noticia => 
            noticia.title?.toLowerCase().includes(lowerBusca) ||
            noticia.description?.toLowerCase().includes(lowerBusca) ||
            noticia.tags?.some((tag: string) => tag.toLowerCase().includes(lowerBusca))
        );
    }, [favoritos, buscaFavoritos]);

    const totalPaginasFavoritos = Math.ceil(favoritosFiltrados.length / noticiasPorPagina);
    const inicioFavoritos = (paginaFavoritos - 1) * noticiasPorPagina;
    const fimFavoritos = inicioFavoritos + noticiasPorPagina;
    const noticiasPaginadasFavoritos = favoritosFiltrados.slice(inicioFavoritos, fimFavoritos);


    // Contagem de notícias (igual)
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

    // Handlers de clique 
    const handleTagClickPortal = (tag: string) => {
        setBuscaPortal(buscaPortal === tag ? "" : tag);
    };

    const handleTagClickFavoritos = (tag: string) => {
        setBuscaFavoritos(buscaFavoritos === tag ? "" : tag);
    };

    const handlePortalChange = (novoPortal: string) => {
        setPortalSelecionado(novoPortal);
        setBuscaPortal(""); // Limpa ambas as buscas
        setBuscaFavoritos("");
    };

    // Agora é uma função que aceita parâmetros
    const getPaginationRange = (totalPages: number, currentPage: number) => {
        const siblingCount = 1;
        const totalPageNumbers = siblingCount + 5; 

        if (totalPageNumbers >= totalPages) {
            return Array.from({ length: totalPages }, (_, i) => i + 1);
        }
        const leftSiblingIndex = Math.max(currentPage - siblingCount, 1);
        const rightSiblingIndex = Math.min(currentPage + siblingCount, totalPages);
        const shouldShowLeftDots = leftSiblingIndex > 2;
        const shouldShowRightDots = rightSiblingIndex < totalPages - 2;
        const firstPageIndex = 1;
        const lastPageIndex = totalPages;

        if (!shouldShowLeftDots && shouldShowRightDots) {
            let leftItemCount = 3 + 2 * siblingCount;
            let leftRange = Array.from({ length: leftItemCount }, (_, i) => i + 1);
            return [...leftRange, "...", totalPages];
        }
        if (shouldShowLeftDots && !shouldShowRightDots) {
            let rightItemCount = 3 + 2 * siblingCount;
            let rightRange = Array.from({ length: rightItemCount }, (_, i) => totalPages - i).reverse();
            return [firstPageIndex, "...", ...rightRange];
        }
        if (shouldShowLeftDots && shouldShowRightDots) {
            let middleRange = Array.from({ length: rightSiblingIndex - leftSiblingIndex + 1 }, (_, i) => leftSiblingIndex + i);
            return [firstPageIndex, "...", ...middleRange, "...", lastPageIndex];
        }
        return [];
    };
    
    // Geradores de números de página
    const pageNumbersPortal = getPaginationRange(totalPaginasPortal, paginaPortal);
    const pageNumbersFavoritos = getPaginationRange(totalPaginasFavoritos, paginaFavoritos);
    
    const RenderNoticiasGrid = ({ noticiasParaRenderizar }: { noticiasParaRenderizar: any[] }) => {
        return (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {noticiasParaRenderizar.map((noticia, idx) => (
                    <Dialog key={idx} open={dialogAberto && noticiaSelecionada === noticia} onOpenChange={(open) => {
                        setDialogAberto(open);
                        if (!open) setNoticiaSelecionada(null);
                    }}>
                        <DialogTrigger asChild>
                            <Card 
                                className="cursor-pointer hover:shadow-lg transition-shadow flex flex-col justify-between min-h-[200px] relative"
                                onClick={() => {
                                    setNoticiaSelecionada(noticia);
                                    setDialogAberto(true);
                                }}
                            >
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    className="absolute top-2 right-2 z-10 h-8 w-8 rounded-full bg-black/10 hover:bg-black/20"
                                    onClick={(e) => {
                                        e.stopPropagation(); 
                                        handleToggleFavorito(noticia);
                                    }}
                                >
                                    <Star className={cn(
                                        "h-5 w-5 text-white transition-all",
                                        isNoticiaFavorita(noticia) 
                                            ? "fill-yellow-400 text-yellow-400" 
                                            : "fill-transparent"
                                    )} />
                                </Button>
                                <div>
                                    <CardHeader>
                                        <CardTitle className="text-lg pr-10">{noticia.title}</CardTitle>
                                    </CardHeader>
                                    {noticia.description && (
                                        <CardContent>
                                            <p className="text-zinc-700 text-sm line-clamp-3 leading-relaxed">{noticia.description}</p>
                                        </CardContent>
                                    )}
                                </div>
                                <CardFooter className="flex flex-col gap-4 pt-4">
                                    <div className="flex flex-row justify-between items-center w-full">
                                        {noticia.date ? (
                                            <span className="text-xs text-zinc-500">
                                                {new Date(noticia.date).toLocaleDateString('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' })}
                                            </span>
                                        ) : <div />}
                                        
                                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                                            <Clock className="w-3 h-3" />
                                            {calcularTempoLeitura(noticia.body || noticia.description)}
                                        </div>
                                    </div>
                                    
                                    {noticia.tags && noticia.tags.length > 0 && (
                                        <div className="flex flex-wrap gap-1 justify-end w-full">
                                            {noticia.tags.slice(0, 2).map((tag: string, tagIdx: number) => (
                                                <Badge key={tagIdx} variant="secondary" className="text-xs">
                                                    {tag}
                                                </Badge>
                                            ))}
                                            {noticia.tags.length > 2 && (
                                                <Badge variant="outline" className="text-xs">
                                                    +{noticia.tags.length - 2}
                                                </Badge>
                                            )}
                                        </div>
                                    )}
                                </CardFooter>
                            </Card>
                        </DialogTrigger>

                        <DialogContent>
                            <DialogHeader>
                                <div className="flex items-center justify-between border-b pb-2 mb-2">
                                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                        <span className="flex items-center gap-1">
                                            <Clock className="w-3 h-3" /> 
                                            {calcularTempoLeitura(noticia.body || noticia.description)} de leitura
                                        </span>
                                    </div>
                                    <div className="flex gap-1 items-center">
                                        <span className="text-xs text-muted-foreground mr-2">Tamanho da fonte:</span>
                                        <Button variant="ghost" size="sm" className="h-6 w-8 p-0 text-xs" onClick={() => setTamanhoFonte("text-sm")}>A-</Button>
                                        <Button variant="ghost" size="sm" className="h-6 w-8 p-0 text-xs font-bold" onClick={() => setTamanhoFonte("text-base")}>A</Button>
                                        <Button variant="ghost" size="sm" className="h-6 w-8 p-0 text-sm font-bold" onClick={() => setTamanhoFonte("text-lg")}>A+</Button>
                                    </div>
                                </div>

                                <DialogTitle>{noticia.title}</DialogTitle>
                                <DialogDescription asChild>
                                    <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm pt-2">
                                        {noticia.date && (
                                            <div className="flex items-center gap-2">
                                                <CalendarDays className="w-4 h-4" />
                                                <span>{new Date(noticia.date).toLocaleDateString('pt-BR', { dateStyle: 'long' })}</span>
                                            </div>
                                        )}
                                        {noticia.tags && noticia.tags.length > 0 && (
                                            <div className="flex items-center gap-2">
                                                <Tags className="w-4 h-4" />
                                                <span className="font-medium">Tags:</span>
                                                <span className="text-zinc-800">{noticia.tags.join(', ')}</span>
                                            </div>
                                        )}
                                    </div>
                                </DialogDescription>
                            </DialogHeader>
                            <div className="p-6 overflow-y-auto">
                                <div className="space-y-6">
                                    {noticia.description && (
                                        <p className={`text-zinc-800 italic leading-relaxed border-l-4 pl-4 ${tamanhoFonte}`}>
                                            {noticia.description}
                                        </p>
                                    )}
                                    {noticia.body && (
                                    <div className="mt-4">
                                        <div 
                                            className="
                                                prose prose-lg max-w-none 
                                                prose-zinc dark:prose-invert
                                                font-serif text-slate-700 dark:text-slate-300
                                                leading-normal
                                                first-letter:text-7xl first-letter:font-bold first-letter:text-black dark:first-letter:text-white first-letter:mr-3 first-letter:float-left first-letter:leading-[0.8]
                                                prose-strong:font-bold prose-strong:text-slate-900 dark:prose-strong:text-slate-100
                                                prose-a:text-blue-600 prose-a:no-underline hover:prose-a:underline
                                                whitespace-pre-line
                                            "
                                            dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(limparLixoVisual(noticia.body)) }} 
                                        />
                                    </div>
                                    )}
                                </div>
                            </div> 
                            {noticia.url && (
                                <DialogFooter className="gap-2">
                                    {/* Botão Copiar Link */}
                                    <Button 
                                        variant="outline" 
                                        onClick={() => handleCopiarLink(noticia.url, noticia.url)} 
                                    >
                                        {copiadoId === noticia.url ? (
                                            <>
                                                <Check className="w-4 h-4 mr-2 text-green-600" />
                                                Copiado!
                                            </>
                                        ) : (
                                            <>
                                                <LinkIcon className="w-4 h-4 mr-2" />
                                                Copiar Link
                                            </>
                                        )}
                                    </Button>

                                    <Button asChild variant="default">
                                        <a href={noticia.url} target="_blank" rel="noopener noreferrer">
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
        );
    };

    // ESTADO DE LOADING (igual)
    if (loading) return (
        <div className="max-w-5xl mx-auto p-8"> 
            <h1 className="text-2xl font-bold mb-4">
                Selecione um portal de notícias
            </h1>
            {/* ... (skeleton) ... */}
            <div className="space-y-6">
                <div className="mx-auto flex w-full max-w-4xl bg-gray-200 rounded-md mb-6">
                    {Array.from({ length: 4 }, (_, idx) => (
                        <div key={idx} className="group flex-1 flex items-center justify-center gap-2 p-3 text-xs">
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
    
    // ESTADO DE ERRO (igual)
    if (erro) return <div className="p-8 text-red-500">{erro}</div>;

    // ESTADO PRINCIPAL (CARREGADO)
    return (
        <div className="max-w-5xl mx-auto p-8">
            <h1 className="text-2xl font-bold mb-4">
                Selecione um portal de notícias
            </h1>
            {portais.length > 0 && (
                <Tabs value={portalSelecionado ?? undefined} onValueChange={handlePortalChange} className="w-full">
                    <TabsList className="mx-auto flex w-full max-w-4xl bg-transparent mb-6 h-auto flex-wrap">
                        <TabsTrigger
                            value="favoritos"
                            className="group data-[state=active]:bg-muted flex-1 flex-col p-3 text-xs data-[state=active]:shadow-none min-w-fit gap-2 items-center"
                        >
                            <Star className="h-10 w-10 text-yellow-500" />
                            <span>Favoritos</span>
                            <Badge className="min-w-5 px-1 transition-opacity group-data-[state=inactive]:opacity-50">
                                {favoritos.length}
                            </Badge>
                        </TabsTrigger>
                        {portais.map((portal) => (
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
                                    {noticiasPorPortal[portal] ?? <Skeleton className="w-3 h-3" />}
                                </Badge>
                            </TabsTrigger>
                        ))}
                    </TabsList>
                    
                    {/* Estado de Boas-Vindas (igual) */}
                    {!portalSelecionado && (
                        <div className="text-center p-16 border-2 border-dashed rounded-lg mt-6 bg-slate-50">
                            <Newspaper className="w-16 h-16 mx-auto mt-4 text-zinc-400 mb-6" />
                            <h2 className="text-2xl font-semibold text-zinc-700 mb-2">
                                Bem-vindo ao seu Agregador de Notícias
                            </h2>
                            <p className="text-lg text-zinc-500">
                                Selecione um portal ou seus favoritos acima.
                            </p>
                        </div>
                    )}

                    {/* Conteúdo dos Portais */}
                    {portais.map((portal) => (
                        <TabsContent key={portal} value={portal}>
                            <div className="mb-2 font-semibold">
                                Portal selecionado: <span className="text-blue-600">{formatarNomePortal(portal)}</span>
                            </div>
                            <div className="flex flex-col md:flex-row gap-8 mt-4">
                                <aside className="w-full md:w-1/4 lg:w-1/5">
                                    <h3 className="font-semibold mb-4 text-lg">Tags Populares</h3>
                                    {carregandoNoticias ? (
                                        <div className="flex flex-wrap gap-2">
                                            {Array.from({ length: 10 }, (_, idx) => <Skeleton key={idx} className="h-6 w-16 rounded-full" />)}
                                        </div>
                                    ) : topTagsPortal.length > 0 ? (
                                        <div className="flex flex-wrap gap-2">
                                            {topTagsPortal.map((tag, idx) => (
                                                <Badge 
                                                    key={idx} 
                                                    variant={buscaPortal === tag ? "default" : "secondary"}
                                                    className="cursor-pointer hover:bg-primary/20 transition-colors"
                                                    onClick={() => handleTagClickPortal(tag)}
                                                >
                                                    {tag}
                                                </Badge>
                                            ))}
                                        </div>
                                    ) : (
                                        <p className="text-sm text-zinc-500">Nenhuma tag encontrada para este portal.</p>
                                    )}
                                </aside>

                                <main className="flex-1">
                                    <div className="relative mb-4">
                                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400" />
                                        <Input
                                            placeholder="Buscar notícias ou clique em uma tag..."
                                            value={buscaPortal}
                                            onChange={(e) => setBuscaPortal(e.target.value)}
                                            className="pl-10 pr-10"
                                        />
                                        {buscaPortal.length > 0 && (
                                            <Button 
                                                variant="ghost" 
                                                size="icon" 
                                                className="absolute right-1 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full"
                                                onClick={() => setBuscaPortal("")}
                                            >
                                                <X className="w-4 h-4" />
                                            </Button>
                                        )}
                                    </div>
                                    {carregandoNoticias ? (
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            {Array.from({ length: 6 }, (_, idx) => (
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
                                    ) : noticiasPaginadasPortal.length === 0 ? (
                                        <div>Nenhuma notícia encontrada{buscaPortal.trim() && ` para "${buscaPortal}"`}.</div>
                                    ) : (
                                        <RenderNoticiasGrid noticiasParaRenderizar={noticiasPaginadasPortal} />
                                    )}

                                    {/* Paginação do PORTAL */}
                                    {totalPaginasPortal > 1 && (
                                        <div className="flex items-center justify-between gap-3 mt-6">
                                            <p className="text-muted-foreground grow text-sm" aria-live="polite">
                                                Página <span className="text-foreground">{paginaPortal}</span> de{" "}
                                                <span className="text-foreground">{totalPaginasPortal}</span>
                                            </p>
                                            <Pagination className="w-auto">
                                                <PaginationContent>
                                                    <PaginationItem>
                                                        <PaginationPrevious
                                                            href="#"
                                                            onClick={(e) => { e.preventDefault(); setPaginaPortal((p) => Math.max(1, p - 1)); }}
                                                            className={paginaPortal === 1 ? "pointer-events-none opacity-50" : undefined}
                                                        />
                                                    </PaginationItem>
                                                    {pageNumbersPortal.map((page, idx) => (
                                                        <PaginationItem key={idx}>
                                                            {typeof page === 'string' ? (
                                                                <PaginationEllipsis />
                                                            ) : (
                                                                <PaginationLink 
                                                                    href="#"
                                                                    onClick={(e) => { e.preventDefault(); setPaginaPortal(page); }}
                                                                    isActive={paginaPortal === page}
                                                                >
                                                                    {page}
                                                                </PaginationLink>
                                                            )}
                                                        </PaginationItem>
                                                    ))}
                                                    <PaginationItem>
                                                        <PaginationNext
                                                            href="#"
                                                            onClick={(e) => { e.preventDefault(); setPaginaPortal((p) => Math.min(totalPaginasPortal, p + 1)); }}
                                                            className={paginaPortal === totalPaginasPortal ? "pointer-events-none opacity-50" : undefined}
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

                    {/* --- CONTEÚDO DA ABA FAVORITOS --- */}
                    <TabsContent value="favoritos">
                        <div className="mb-2 font-semibold">
                            Seção selecionada: <span className="text-yellow-600">Favoritos</span>
                        </div>
                        
                        {favoritos.length === 0 ? (
                            <div className="text-center p-16 border-2 border-dashed rounded-lg mt-6 bg-slate-50">
                                <Frown className="w-16 h-16 mx-auto mt-4 text-zinc-400 mb-6" />
                                <h2 className="text-2xl font-semibold text-zinc-700 mb-2">
                                    Nenhum favorito salvo
                                </h2>
                                <p className="text-lg text-zinc-500">
                                    Clique na estrela ( <Star className="w-4 h-4 inline-block" /> ) em qualquer notícia para salvá-la aqui.
                                </p>
                            </div>
                        ) : (
                            // Layout de 2 colunas para favoritos
                            <div className="flex flex-col md:flex-row gap-8 mt-4">
                                <aside className="w-full md:w-1/4 lg:w-1/5">
                                    <h3 className="font-semibold mb-4 text-lg">Tags Salvas</h3>
                                    {topTagsFavoritos.length > 0 ? (
                                        <div className="flex flex-wrap gap-2">
                                            {topTagsFavoritos.map((tag, idx) => (
                                                <Badge 
                                                    key={idx} 
                                                    variant={buscaFavoritos === tag ? "default" : "secondary"}
                                                    className="cursor-pointer hover:bg-primary/20 transition-colors"
                                                    onClick={() => handleTagClickFavoritos(tag)}
                                                >
                                                    {tag}
                                                </Badge>
                                            ))}
                                        </div>
                                    ) : (
                                        <p className="text-sm text-zinc-500">Nenhuma tag encontrada nos seus favoritos.</p>
                                    )}
                                </aside>

                                <main className="flex-1">
                                    <div className="relative mb-4">
                                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400" />
                                        <Input
                                            placeholder="Buscar nos seus favoritos..."
                                            value={buscaFavoritos}
                                            onChange={(e) => setBuscaFavoritos(e.target.value)}
                                            className="pl-10 pr-10"
                                        />
                                        {buscaFavoritos.length > 0 && (
                                            <Button 
                                                variant="ghost" 
                                                size="icon" 
                                                className="absolute right-1 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full"
                                                onClick={() => setBuscaFavoritos("")}
                                            >
                                                <X className="w-4 h-4" />
                                            </Button>
                                        )}
                                    </div>

                                    {favoritosFiltrados.length === 0 ? (
                                        <div>Nenhum favorito encontrado{buscaFavoritos.trim() && ` para "${buscaFavoritos}"`}.</div>
                                    ) : (
                                        <RenderNoticiasGrid noticiasParaRenderizar={noticiasPaginadasFavoritos} />
                                    )}

                                    {/* Paginação dos FAVORITOS */}
                                    {totalPaginasFavoritos > 1 && (
                                        <div className="flex items-center justify-between gap-3 mt-6">
                                            <p className="text-muted-foreground grow text-sm" aria-live="polite">
                                                Página <span className="text-foreground">{paginaFavoritos}</span> de{" "}
                                                <span className="text-foreground">{totalPaginasFavoritos}</span>
                                            </p>
                                            <Pagination className="w-auto">
                                                <PaginationContent>
                                                    <PaginationItem>
                                                        <PaginationPrevious
                                                            href="#"
                                                            onClick={(e) => { e.preventDefault(); setPaginaFavoritos((p) => Math.max(1, p - 1)); }}
                                                            className={paginaFavoritos === 1 ? "pointer-events-none opacity-50" : undefined}
                                                        />
                                                    </PaginationItem>
                                                    {pageNumbersFavoritos.map((page, idx) => (
                                                        <PaginationItem key={idx}>
                                                            {typeof page === 'string' ? (
                                                                <PaginationEllipsis />
                                                            ) : (
                                                                <PaginationLink 
                                                                    href="#"
                                                                    onClick={(e) => { e.preventDefault(); setPaginaFavoritos(page); }}
                                                                    isActive={paginaFavoritos === page}
                                                                >
                                                                    {page}
                                                                </PaginationLink >
                                                            )}
                                                        </PaginationItem>
                                                    ))}
                                                    <PaginationItem>
                                                        <PaginationNext
                                                            href="#"
                                                            onClick={(e) => { e.preventDefault(); setPaginaFavoritos((p) => Math.min(totalPaginasFavoritos, p + 1)); }}
                                                            className={paginaFavoritos === totalPaginasFavoritos ? "pointer-events-none opacity-50" : undefined}
                                                        />
                                                    </PaginationItem>
                                                </PaginationContent>
                                            </Pagination>
                                        </div>
                                    )}
                                </main>
                            </div>
                        )}
                    </TabsContent>
                </Tabs>
            )}
        </div>
    );
};

export default Home;