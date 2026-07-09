import React from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { EmptyState } from "./EmptyState";

export interface ColumnDef<T> {
  key: string | keyof T;
  header: string | React.ReactNode;
  cell?: (item: T) => React.ReactNode;
  align?: "left" | "center" | "right";
}

interface DataTableProps<T> {
  data: T[];
  columns: ColumnDef<T>[];
  emptyTitle?: string;
  emptyDescription?: string;
}

export function DataTable<T>({ data, columns, emptyTitle = "No Data", emptyDescription = "There is no data to display." }: DataTableProps<T>) {
  if (!data || data.length === 0) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />;
  }

  return (
    <div className="rounded-md border bg-card">
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map((col, idx) => (
              <TableHead key={String(col.key) + idx} className={col.align === "right" ? "text-right" : col.align === "center" ? "text-center" : ""}>
                {col.header}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((item, rowIndex) => (
            <TableRow key={rowIndex}>
              {columns.map((col, colIndex) => (
                <TableCell key={String(col.key) + colIndex} className={col.align === "right" ? "text-right" : col.align === "center" ? "text-center" : ""}>
                  {col.cell ? col.cell(item) : String(item[col.key as keyof T] ?? "")}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
