import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, Sparkles, Shield, ArrowRight } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

interface DocumentUploadProps {
  onFileSelected?: (file: { name: string; size: string; isPreset?: boolean }) => void;
  title?: string;
  subtitle?: string;
  acceptedFormats?: string;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onFileSelected,
  title = "Upload Official Government Circular or Document",
  subtitle = "Supports PDF, Scanned Gazette Circulars, State Notifications (Max 15MB)",
  acceptedFormats = ".pdf, .png, .jpg, .jpeg"
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<{ name: string; size: string; isPreset?: boolean } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const samplePresets = [
    {
      name: "Karnataka_Raita_Vidya_Nidhi_Gazette_Circular_2024.pdf",
      size: "1.42 MB",
      label: "Sample 1: Karnataka Raita Vidya Nidhi"
    },
    {
      name: "PM_KUSUM_Component_B_Guidelines_2024.pdf",
      size: "2.18 MB",
      label: "Sample 2: PM-KUSUM Solar Pumps"
    },
    {
      name: "Central_Post_Matric_Scholarship_Norms.pdf",
      size: "980 KB",
      label: "Sample 3: Central Post-Matric SC/ST"
    }
  ];

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      const sizeMb = (file.size / (1024 * 1024)).toFixed(2) + ' MB';
      const fileObj = { name: file.name, size: sizeMb, isPreset: false };
      setSelectedFile(fileObj);
      if (onFileSelected) onFileSelected(fileObj);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const sizeMb = (file.size / (1024 * 1024)).toFixed(2) + ' MB';
      const fileObj = { name: file.name, size: sizeMb, isPreset: false };
      setSelectedFile(fileObj);
      if (onFileSelected) onFileSelected(fileObj);
    }
  };

  const handleSelectPreset = (preset: { name: string; size: string }) => {
    const fileObj = { name: preset.name, size: preset.size, isPreset: true };
    setSelectedFile(fileObj);
    if (onFileSelected) onFileSelected(fileObj);
  };

  return (
    <div className="space-y-4">
      {/* Upload Zone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-2xl p-6 sm:p-8 text-center cursor-pointer transition-all duration-200 ${
          dragActive 
            ? 'border-govgreen-500 bg-govgreen-50/70 scale-[0.99]' 
            : selectedFile
            ? 'border-emerald-300 bg-emerald-50/30'
            : 'border-slate-300 hover:border-govgreen-400 bg-white hover:bg-slate-50/60'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={acceptedFormats}
          onChange={handleChange}
          className="hidden"
        />

        <div className="max-w-md mx-auto flex flex-col items-center">
          <div className="w-14 h-14 rounded-2xl bg-govgreen-50 text-govgreen-700 flex items-center justify-center mb-3 shadow-subtle border border-govgreen-200/60">
            {selectedFile ? (
              <FileText className="w-7 h-7 text-govgreen-700" />
            ) : (
              <UploadCloud className="w-7 h-7 text-govgreen-700" />
            )}
          </div>

          <h4 className="text-base font-bold text-charcoal-900">
            {selectedFile ? selectedFile.name : title}
          </h4>

          <p className="text-xs text-slate-500 mt-1 max-w-sm">
            {selectedFile ? `File size: ${selectedFile.size} • Ready for analysis` : subtitle}
          </p>

          {!selectedFile && (
            <div className="mt-4">
              <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-govgreen-800 bg-govgreen-100/70 hover:bg-govgreen-100 px-4 py-2 rounded-lg border border-govgreen-200 shadow-subtle transition">
                <span>Browse Files</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </span>
            </div>
          )}

          {selectedFile && (
            <div className="mt-3 flex items-center gap-2">
              <span className="text-xs font-semibold text-emerald-800 bg-emerald-100 px-3 py-1 rounded-full flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                Document Attached
              </span>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedFile(null);
                }}
                className="text-xs text-slate-500 hover:text-rose-600 underline"
              >
                Remove
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Preset Demo Circulars for Quick Evaluation */}
      <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-purple-600" />
            Or Try Pre-Loaded Real Government Circulars (Demo)
          </span>
          <StatusBadge status="demo" label="Preset Sample" />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          {samplePresets.map((preset, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSelectPreset(preset)}
              className="text-left p-2.5 rounded-lg bg-white hover:bg-govgreen-50/70 border border-slate-200 hover:border-govgreen-300 transition text-xs group"
            >
              <div className="font-semibold text-slate-800 group-hover:text-govgreen-900 truncate">
                {preset.label}
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">
                {preset.size} • Official PDF
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Privacy Guarantee */}
      <div className="flex items-center gap-2 text-[11px] text-slate-500 justify-center">
        <Shield className="w-3.5 h-3.5 text-govgreen-700 flex-shrink-0" />
        <span>Client-side parsing &amp; secure processing. No citizen documents are retained without consent.</span>
      </div>
    </div>
  );
};
