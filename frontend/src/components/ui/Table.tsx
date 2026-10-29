import React from 'react';

export interface TableProps extends React.TableHTMLAttributes<HTMLTableElement> {
  compact?: boolean;
}

export const Table: React.FC<TableProps> = ({
  children,
  className = '',
  compact = false,
  ...props
}) => {
  return (
    <div className="w-full overflow-x-auto border border-border rounded-lg bg-surface">
      <table className={`w-full text-left text-xs text-content-secondary ${className}`} {...props}>
        {children}
      </table>
    </div>
  );
};

export const Thead: React.FC<React.HTMLAttributes<HTMLTableSectionElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <thead className={`bg-surface-elevated/80 border-b border-border text-[11px] font-mono uppercase tracking-wider text-content-muted ${className}`} {...props}>
    {children}
  </thead>
);

export const Tbody: React.FC<React.HTMLAttributes<HTMLTableSectionElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <tbody className={`divide-y divide-border ${className}`} {...props}>
    {children}
  </tbody>
);

export const Tr: React.FC<React.HTMLAttributes<HTMLTableRowElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <tr className={`transition-colors duration-100 hover:bg-surface-elevated/40 ${className}`} {...props}>
    {children}
  </tr>
);

export const Th: React.FC<React.ThHTMLAttributes<HTMLTableCellElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <th className={`px-4 py-3 font-semibold ${className}`} {...props}>
    {children}
  </th>
);

export const Td: React.FC<React.TdHTMLAttributes<HTMLTableCellElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <td className={`px-4 py-3 text-content-primary ${className}`} {...props}>
    {children}
  </td>
);

export const TableHeader = Thead;
export const TableBody = Tbody;
export const TableRow = Tr;
export const TableHead = Th;
export const TableCell = Td;
