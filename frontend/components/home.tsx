"use client";

import { DragNDrop } from "@/components/drag-drop";

export default function Home() {
  return (
    <div className="flex justify-center items-center h-screen">

      {/* Name Plate */}
      <div className="flex flex-col items-center -mt-24">
        <div className="w-full">
          <div className="flex items-center gap-x-3 mb-4">
            <h1 className="text-5xl font-extralight" style={{ fontFamily: 'Helvetica, sans-serif' }}>
              Pamphlets
            </h1>
            
            <p className="text-lg text-gray-600 font-light" style={{ fontFamily: 'Helvetica, sans-serif' }}>
              Effortlessly share documents
            </p>
          </div>
        </div>
        {/* Drag N Drop */}
        <div className="mt-4 max-w-lg mx-auto">
          <DragNDrop/>
        </div>
      </div>
    </div>
  );
}