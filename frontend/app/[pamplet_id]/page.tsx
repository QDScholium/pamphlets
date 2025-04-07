"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import rehypeRaw from 'rehype-raw';

export default function PampletPage() {
  const params = useParams();
  const pampletId = params.pamplet_id;
  const [content, setContent] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchPampletContent() {
      try {
        const response = await fetch(`http://localhost:8000/articles/${pampletId}`);
        if (!response.ok) {
          throw new Error(`Failed to fetch pamplet: ${response.statusText}`);
        }
        const data = await response.json();
        setContent(data.pages);
      } catch (err) {
        console.error("Error fetching pamplet:", err);
        setError(err instanceof Error ? err.message : "Failed to load pamplet");
      } finally {
        setLoading(false);
      }
    }

    if (pampletId) {
      fetchPampletContent();
    }
  }, [pampletId]);

  return (
    <div className="container mx-auto py-8 px-4 flex flex-col items-center justify-center">
      {loading && <p className="text-gray-600 text-center">Loading pamplet content...</p>}
      {error && <p className="text-red-500">Error: {error}</p>}
      
      {content && (
        <div className="mt-4 w-full max-w-3xl">
          {Array.isArray(content) && content.map((page, index) => (
            <div key={index} className="mb-8">
                <div className="leading-relaxed">
                <ReactMarkdown
                    className="whitespace-pre-line prose prose-headings:font-light prose-h1:text-3xl prose-h2:text-2xl prose-h3:text-xl prose-h4:text-lg prose-h5:text-base prose-h6:text-sm"
                    rehypePlugins={[rehypeRaw as any]}
                    skipHtml={false}
                    components={{
                        h1: ({ children }: React.PropsWithChildren) => <h1 className="text-3xl font-light mt-6 mb-4">{children}</h1>,
                        h2: ({ children }: React.PropsWithChildren) => <h2 className="text-2xl font-light mt-5 mb-3">{children}</h2>,
                        h3: ({ children }: React.PropsWithChildren) => <h3 className="text-xl font-light mt-4 mb-2">{children}</h3>,
                        h4: ({ children }: React.PropsWithChildren) => <h4 className="text-lg font-light mt-3 mb-2">{children}</h4>,
                        h5: ({ children }: React.PropsWithChildren) => <h5 className="text-base font-light mt-2 mb-1">{children}</h5>,
                        h6: ({ children }: React.PropsWithChildren) => <h6 className="text-sm font-light mt-2 mb-1">{children}</h6>,
                        p: ({ children }: React.PropsWithChildren) => <p className="my-2">{children}</p>,
                        ul: ({ children }: React.PropsWithChildren) => <ul className="list-disc pl-6 my-3">{children}</ul>,
                        ol: ({ children }: React.PropsWithChildren) => <ol className="list-decimal pl-6 my-3">{children}</ol>,
                        li: ({ children }: React.PropsWithChildren) => <li className="my-1">{children}</li>,
                        a: ({ href, children }: React.PropsWithChildren<{href?: string}>) => <a href={href} className="text-blue-600 hover:underline">{children}</a>,
                        blockquote: ({ children }: React.PropsWithChildren) => <blockquote className="border-l-4 border-gray-300 pl-4 italic my-4">{children}</blockquote>,
                        code: ({ children }: React.PropsWithChildren) => <code className="bg-gray-100 px-1 py-0.5 rounded font-mono text-sm">{children}</code>
                    }}
                >
                    {page.markdown}
                </ReactMarkdown>
                {/* <hr className="my-6 border-t border-black" /> */}
                <div style={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                <div style={{ flex: 1, height: '1px', backgroundColor: '#000' }} />
                <span style={{ margin: '0 10px' }}>{index+1}</span>
                <div style={{ flex: 1, height: '1px', backgroundColor: '#000' }} />
                </div>
                </div>
            </div>
            ))}
        </div>
      )}
    </div>
  );
}
