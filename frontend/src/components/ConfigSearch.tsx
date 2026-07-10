import React, { useState, useEffect, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { configurationApi } from "@/api";
import { Search, Loader2, Check } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface ConfigSearchProps {
  onSelect: (configId: string) => void;
  selectedId?: string | null;
  placeholder?: string;
  className?: string;
}

export function ConfigSearch({ onSelect, selectedId, placeholder = "Search configuration ID or project...", className = "" }: ConfigSearchProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const containerRef = useRef<HTMLDivElement>(null);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(searchTerm), 300);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  const { data: searchResults, isLoading } = useQuery({
    queryKey: ["configurations", "search", debouncedSearch],
    queryFn: () => configurationApi.search(debouncedSearch, 10),
    enabled: isOpen, // Only fetch when dropdown is open
  });

  // Handle outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const results = Array.isArray(searchResults) ? searchResults : [];

  return (
    <div className={`relative w-full z-50 ${className}`} ref={containerRef}>
      <div 
        className="relative flex items-center w-full border rounded-md bg-background focus-within:ring-2 focus-within:ring-primary/50"
        onClick={() => setIsOpen(true)}
      >
        <Search className="absolute left-3 w-4 h-4 text-muted-foreground" />
        <input
          type="text"
          className="w-full pl-9 pr-4 py-2 text-sm bg-transparent outline-none"
          placeholder={selectedId || placeholder}
          value={searchTerm}
          onChange={(e) => {
            const val = e.target.value;
            setSearchTerm(val);
            setIsOpen(true);
            onSelect(val);
          }}
          onFocus={() => setIsOpen(true)}
        />
        {isLoading && <Loader2 className="absolute right-3 w-4 h-4 animate-spin text-muted-foreground" />}
      </div>

      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-card border rounded-md shadow-lg z-50 max-h-64 overflow-y-auto">
          {results.length === 0 && !isLoading ? (
            <div className="p-4 text-center text-sm text-muted-foreground">
              No configurations found.
            </div>
          ) : (
            <ul className="py-1">
              {results.map((item: any) => (
                <li
                  key={item.configuration_id}
                  className={`px-4 py-2 text-sm cursor-pointer flex justify-between items-center hover:bg-muted/50 ${selectedId === item.configuration_id ? "bg-muted" : ""}`}
                  onClick={() => {
                    onSelect(item.configuration_id);
                    setIsOpen(false);
                    setSearchTerm(""); // clear search to show selected ID in placeholder
                  }}
                >
                  <div>
                    <div className="font-medium flex items-center gap-2">
                      <span className="text-muted-foreground text-xs font-mono">#{item.display_id}</span>
                      {item.project_name || "Unnamed Project"}
                    </div>
                    <div className="text-xs text-muted-foreground font-mono mt-0.5">
                      {item.configuration_id}
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <Badge variant="outline" className="text-[10px] h-4 leading-3 px-1">{item.status}</Badge>
                    {selectedId === item.configuration_id && <Check className="w-3 h-3 text-primary" />}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
