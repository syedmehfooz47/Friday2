// jarvis-ui/app/files/_comps/GeneratedFilesDisplay.tsx

"use client";

import { memo, useState, useEffect } from "react";
import { FrostedCard } from "@/app/(dashboard)/_comps/ui/FrostedCard";
import { CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import {
    FolderOpen, FileText, FileImage, FileSpreadsheet, FileArchive,
    FileQuestion, RefreshCw, Search, ExternalLink,
    FileAudio, FileVideo, Presentation, AlertTriangle
} from "lucide-react";
import { formatDistanceToNow } from 'date-fns';

const API_BASE_URL = "http://localhost:8000/api";

interface GeneratedFile {
    name: string;
    path: string;
    type: 'document' | 'image' | 'spreadsheet' | 'presentation' | 'archive' | 'text' | 'audio' | 'video' | 'unknown';
    size: number;
    modified: string;
}

const getFileExtension = (fileName: string): string => {
    const parts = fileName.split('.');
    return parts.length > 1 ? `.${parts[parts.length - 1].toLowerCase()}` : '';
};

const getFileInfo = (fileName: string): { icon: React.ElementType, type: GeneratedFile['type'], color: string } => {
    const extension = getFileExtension(fileName);
    switch (extension) {
        case '.pdf':
        case '.docx':
        case '.doc':
            return { icon: FileText, type: 'document', color: 'text-blue-500 dark:text-blue-400' };
        case '.pptx':
        case '.ppt':
            return { icon: Presentation, type: 'presentation', color: 'text-orange-500 dark:text-orange-400' };
        case '.xlsx':
        case '.xls':
        case '.csv':
            return { icon: FileSpreadsheet, type: 'spreadsheet', color: 'text-green-500 dark:text-green-400' };
        case '.jpg':
        case '.jpeg':
        case '.png':
        case '.gif':
        case '.webp':
        case '.svg':
        case '.bmp':
        case '.tiff':
            return { icon: FileImage, type: 'image', color: 'text-purple-500 dark:text-purple-400' };
        case '.zip':
        case '.rar':
        case '.7z':
            return { icon: FileArchive, type: 'archive', color: 'text-yellow-500 dark:text-yellow-400' };
        case '.txt':
        case '.log':
        case '.md':
            return { icon: FileText, type: 'text', color: 'text-gray-500 dark:text-gray-400'};
        case '.mp3':
        case '.wav':
        case '.ogg':
            return { icon: FileAudio, type: 'audio', color: 'text-pink-500 dark:text-pink-400'};
        case '.mp4':
        case '.avi':
        case '.mov':
        case '.mkv':
            return { icon: FileVideo, type: 'video', color: 'text-red-500 dark:text-red-400' };
        default:
            return { icon: FileQuestion, type: 'unknown', color: 'text-gray-400 dark:text-gray-500' };
    }
};

const formatFileSize = (bytes: number): string => {
    if (bytes < 0) return 'N/A';
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    const size = parseFloat((bytes / Math.pow(k, i)).toFixed(1));
    return (size < 0.1 && i > 0 ? 0.1 : size) + ' ' + sizes[i];
};

const FileItem = memo(({ file, onOpenFile }: { file: GeneratedFile, onOpenFile: (path: string) => void }) => {
    const { icon: Icon, color } = getFileInfo(file.name);
    let relativeTime = 'unknown time';
    try {
        relativeTime = formatDistanceToNow(new Date(file.modified), { addSuffix: true });
    } catch (e) { 
        console.error("Invalid date for file:", file.name, file.modified); 
    }

    return (
        <div className="flex items-center justify-between p-3 bg-white/50 dark:bg-black/20 rounded-lg shadow-sm hover:bg-white/70 dark:hover:bg-black/30 transition-colors duration-150 group">
            <div className="flex items-center overflow-hidden space-x-3 flex-1 min-w-0">
                <Icon className={`h-7 w-7 flex-shrink-0 ${color}`} />
                <div className="overflow-hidden">
                    <p className="text-sm font-medium text-slate-800 dark:text-slate-100 truncate group-hover:underline" title={file.name}>
                        {file.name}
                    </p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                        {relativeTime} &bull; {formatFileSize(file.size)}
                    </p>
                </div>
            </div>
            <div className="flex-shrink-0 space-x-1 ml-2">
                <Button 
                    variant="ghost" 
                    size="icon" 
                    className="h-8 w-8 text-slate-500 hover:text-cyan-600 dark:hover:text-cyan-400" 
                    title="Open File" 
                    onClick={() => onOpenFile(file.path)}
                >
                    <ExternalLink className="h-4 w-4" />
                </Button>
            </div>
        </div>
    );
});

FileItem.displayName = 'FileItem';

export default function GeneratedFilesDisplay() {
    const [files, setFiles] = useState<GeneratedFile[]>([]);
    const [filteredFiles, setFilteredFiles] = useState<GeneratedFile[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState("");
    const [filterType, setFilterType] = useState<GeneratedFile['type'] | 'all'>("all");

    const fetchFiles = async () => {
        setIsLoading(true);
        setError(null);
        console.log("Fetching generated files...");
        try {
            const response = await fetch(`${API_BASE_URL}/generated-files`);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: `HTTP error ${response.status}` }));
                throw new Error(errorData.error || 'Failed to fetch files');
            }
            const data = await response.json();
            const fetchedFiles: GeneratedFile[] = Array.isArray(data.files) ? data.files : [];

            const typedFiles = fetchedFiles.map(f => ({...f, type: getFileInfo(f.name).type }));

            setFiles(typedFiles);
            console.log(`Fetched ${typedFiles.length} files`);
        } catch (err: any) {
            setError(err.message || "An error occurred while fetching files.");
            toast.error("Failed to load files", { description: err.message });
            console.error("Fetch files error:", err);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchFiles();
    }, []);

    useEffect(() => {
        let currentFiles = files;

        if (filterType !== "all") {
            currentFiles = currentFiles.filter(file => file.type === filterType);
        }

        if (searchTerm) {
            const lowerSearchTerm = searchTerm.toLowerCase();
            currentFiles = currentFiles.filter(file =>
                file.name.toLowerCase().includes(lowerSearchTerm)
            );
        }

        setFilteredFiles(currentFiles);
    }, [searchTerm, filterType, files]);

    const handleOpenFile = async (filePath: string) => {
        const fileName = filePath.split('/').pop() || filePath.split('\\').pop() || filePath;
        toast.info("Opening file...", { description: `Requesting to open: ${fileName}` });
        try {
            const response = await fetch(`${API_BASE_URL}/open-file`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: filePath })
            });
            const result = await response.json();
            if (!response.ok || !result.success) {
                throw new Error(result.error || 'Backend failed to open file');
            }
            console.log("File open request successful for:", filePath);
        } catch (error: any) {
            toast.error("Failed to open file", { description: error.message });
            console.error("Open file error:", error);
        }
    };

    const fileTypes: GeneratedFile['type'][] = ['document', 'presentation', 'spreadsheet', 'image', 'text', 'archive', 'audio', 'video', 'unknown'];

    return (
        <div className="p-4 sm:p-6 lg:p-8 h-full flex flex-col">
            <div className="flex items-center justify-between mb-6 flex-shrink-0">
                <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100 flex items-center">
                    <FolderOpen className="w-7 h-7 mr-3 text-cyan-500" />
                    Generated & Converted Files
                </h1>
                <Button 
                    variant="ghost" 
                    size="icon" 
                    onClick={fetchFiles} 
                    disabled={isLoading} 
                    className="h-9 w-9 text-slate-500 hover:bg-slate-200 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed" 
                    title="Refresh Files"
                >
                    <RefreshCw className={`h-5 w-5 ${isLoading ? 'animate-spin text-cyan-500' : ''}`} />
                </Button>
            </div>

            <div className="flex flex-col md:flex-row gap-4 mb-4 flex-shrink-0">
                <div className="relative flex-grow">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none" />
                    <Input
                        type="search"
                        placeholder="Search by filename..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10 bg-white/50 dark:bg-black/20 border-slate-200 dark:border-white/10 focus:ring-cyan-500 focus:border-cyan-500 h-10"
                        disabled={isLoading}
                        aria-label="Search generated files"
                    />
                </div>
                <Select value={filterType} onValueChange={(value) => setFilterType(value as GeneratedFile['type'] | 'all')} disabled={isLoading}>
                    <SelectTrigger className="w-full md:w-[180px] bg-white/50 dark:bg-black/20 border-slate-200 dark:border-white/10 h-10">
                        <SelectValue placeholder="Filter by type..." />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">All Types</SelectItem>
                        {fileTypes.map(type => (
                            <SelectItem key={type} value={type} className="capitalize">{type}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </div>

            <FrostedCard className="flex-grow overflow-hidden flex flex-col">
                <CardContent className="p-3 h-full flex-grow overflow-hidden">
                    {isLoading ? (
                        <div className="flex justify-center items-center h-full text-slate-500 animate-pulse">Loading files...</div>
                    ) : error ? (
                        <div className="flex flex-col justify-center items-center h-full text-center text-red-500 p-4">
                            <AlertTriangle className="w-10 h-10 mb-3" />
                            <p className="font-semibold text-lg">Error Loading Files</p>
                            <p className="text-sm mt-1 mb-4">{error}</p>
                            <Button variant="outline" size="sm" onClick={fetchFiles}>Retry</Button>
                        </div>
                    ) : filteredFiles.length === 0 ? (
                        <div className="flex justify-center items-center h-full text-slate-500 dark:text-slate-400 text-center p-4">
                            {searchTerm || filterType !== 'all'
                                ? 'No files found matching your filters.'
                                : 'No generated or converted files found in the Data directory.'
                            }
                        </div>
                    ) : (
                        <ScrollArea className="h-full pr-3">
                            <div className="space-y-2">
                                {filteredFiles.map((file) => (
                                    <FileItem key={file.path} file={file} onOpenFile={handleOpenFile} />
                                ))}
                            </div>
                        </ScrollArea>
                    )}
                </CardContent>
            </FrostedCard>
        </div>
    );
}