"use client";

import { useState } from "react";
import { 
  Network, Rocket, Download, CheckCircle2, 
  AlertCircle, Info, Search, ShieldCheck, 
  AlertTriangle, Eye, FileCode, ChevronRight,
  ChevronDown, Check, X // <--- Add these
} from "lucide-react";
// UI Components (Assuming you have these installed via shadcn/ui)
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Separator } from "@/components/ui/separator";

const API_BASE = "http://localhost:8000";

// --- TYPES (For Safety) ---
interface Issue {
  rule: string;
  description: string;
  wcag_sc?: string;
  fix_priority: string;
  selector?: string;
  html_snippet?: string;
  ai_explanation?: string;
  ai_fixed_code?: string;
  is_vision?: boolean;
}

interface AuditSummary {
  total: number;
  critical: number;
  serious: number;
  minor: number;
  india_compliance: string;
  status: string;
}

interface AuditData {
  summary: AuditSummary;
  report: Issue[];
  error?: string;
}

export default function Home() {
  // State
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [url, setUrl] = useState("https://dequeuniversity.com/demo/mars/");
  const [crawledPages, setCrawledPages] = useState<string[]>([]);
  const [selectedPages, setSelectedPages] = useState<string[]>([]);
  const [auditResults, setAuditResults] = useState<Record<string, AuditData>>({});
  
  // UI State
  const [isCrawling, setIsCrawling] = useState(false);
  const [isAuditing, setIsAuditing] = useState(false);
  const [auditProgress, setAuditProgress] = useState(0);
  const [searchTerm, setSearchTerm] = useState("");

  // --- ACTIONS ---

  const startCrawl = async () => {
    if (!url) return;
    setIsCrawling(true);
    try {
      const res = await fetch(`${API_BASE}/crawl`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, max_pages: 10 }),
      });
      if (!res.ok) throw new Error("Failed");
      const data = await res.json();
      
      const pages = data.urls || [];
      setCrawledPages(pages);
      setSelectedPages(pages.slice(0, 1)); // Default select first
      setAuditResults({}); // Clear old
    } catch (err) {
      alert("Crawler failed. Ensure Backend is running on Port 8000.");
    }
    setIsCrawling(false);
  };

  const runAudit = async () => {
    if (selectedPages.length === 0) return;
    setIsAuditing(true);
    setAuditProgress(0);
    const results: Record<string, AuditData> = {};

    for (let i = 0; i < selectedPages.length; i++) {
      const page = selectedPages[i];
      try {
        const res = await fetch(`${API_BASE}/audit`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: page }),
        });
        const data = await res.json();
        results[page] = data;
      } catch (err) {
        console.error(err);
        // @ts-ignore
        results[page] = { summary: {}, report: [], error: "Failed to audit page" };
      }
      setAuditProgress(((i + 1) / selectedPages.length) * 100);
    }

    setAuditResults(results);
    setIsAuditing(false);
  };

  return (
    <div className="min-h-screen bg-slate-50 pb-20 font-sans text-slate-900">
      
      {/* 1. Navbar */}
      <nav className="bg-white border-b sticky top-0 z-20 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-blue-600 p-1.5 rounded-lg">
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-xl tracking-tight">EmpathAI v2.0</span>
            <Badge variant="outline" className="ml-2 text-xs font-normal bg-slate-50">Enterprise</Badge>
          </div>
          <div className="text-sm text-slate-500">Autonomous Accessibility Auditor</div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-6 space-y-8 mt-4">
        
        {/* 2. Discovery Section */}
        <Card className="border-slate-200 shadow-sm">
          <CardHeader className="bg-slate-50/50 border-b pb-4">
            <CardTitle className="flex items-center gap-2 text-lg text-blue-700">
              <Network className="w-5 h-5" />
              1. Discovery Phase
            </CardTitle>
            <CardDescription>Enter a root URL to map the website structure.</CardDescription>
          </CardHeader>
          <CardContent className="p-6">
            <div className="flex gap-3 max-w-3xl">
              <Input
                placeholder="https://example.com"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="h-11 text-base shadow-sm"
                onKeyDown={(e) => e.key === "Enter" && startCrawl()}
              />
              <Button 
                onClick={startCrawl} 
                disabled={isCrawling} 
                size="lg" 
                className="bg-blue-600 hover:bg-blue-700 h-11"
              >
                {isCrawling ? "Scanning..." : "Start Discovery"}
              </Button>
            </div>
          </CardContent>
        </Card>

      {/* 3. Page Selection (Dropdown Style) */}
        {crawledPages.length > 0 && (
          <Card className="border-slate-200 shadow-sm animate-in fade-in slide-in-from-bottom-3 overflow-visible">
            <CardHeader className="bg-slate-50/50 border-b pb-4">
              <div className="flex justify-between items-center">
                <CardTitle className="text-lg">2. Select Pages</CardTitle>
                <Badge variant="secondary">{selectedPages.length} Selected</Badge>
              </div>
            </CardHeader>
            <CardContent className="p-6 space-y-6 overflow-visible">
              
              {/* Custom Multi-Select Dropdown */}
              <div className="relative">
                <label className="text-sm font-medium text-slate-700 mb-1.5 block">
                  Choose pages to audit:
                </label>
                
                <button 
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  className="w-full flex items-center justify-between px-4 py-3 bg-white border border-slate-300 rounded-lg text-left shadow-sm hover:border-blue-400 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <span className="text-slate-700">
                    {selectedPages.length === 0 
                      ? "Select pages..." 
                      : selectedPages.length === crawledPages.length 
                        ? "All Pages Selected" 
                        : `${selectedPages.length} pages selected`}
                  </span>
                  <ChevronDown className={`w-5 h-5 text-slate-400 transition-transform ${isDropdownOpen ? "rotate-180" : ""}`} />
                </button>

                {/* Dropdown Menu */}
                {isDropdownOpen && (
                  <div className="absolute z-50 w-full mt-2 bg-white border border-slate-200 rounded-lg shadow-xl max-h-80 overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-100">
                    
                    {/* Toolbar */}
                    <div className="p-2 border-b bg-slate-50 flex gap-2 sticky top-0">
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="w-full text-xs h-8"
                        onClick={() => setSelectedPages([...crawledPages])}
                      >
                        Select All
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="w-full text-xs h-8"
                        onClick={() => setSelectedPages([])}
                      >
                        Clear
                      </Button>
                    </div>

                    {/* List */}
                    <div className="overflow-y-auto p-2 space-y-1">
                      {crawledPages.map((page) => {
                        const isSelected = selectedPages.includes(page);
                        return (
                          <div 
                            key={page}
                            onClick={() => {
                              if (isSelected) setSelectedPages(selectedPages.filter(p => p !== page));
                              else setSelectedPages([...selectedPages, page]);
                            }}
                            className={`
                              flex items-center px-3 py-2.5 rounded-md cursor-pointer text-sm transition-colors
                              ${isSelected ? "bg-blue-50 text-blue-700 font-medium" : "text-slate-600 hover:bg-slate-50"}
                            `}
                          >
                            <div className={`
                              w-5 h-5 rounded border flex items-center justify-center mr-3 transition-colors
                              ${isSelected ? "bg-blue-600 border-blue-600" : "border-slate-300 bg-white"}
                            `}>
                              {isSelected && <Check className="w-3.5 h-3.5 text-white" />}
                            </div>
                            <span className="truncate">{page.replace(/^https?:\/\//, "")}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>

              {/* Tags Display (Shows what is selected) */}
              {selectedPages.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-4">
                  {selectedPages.slice(0, 5).map(page => (
                    <span key={page} className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
                      {page.replace(/^https?:\/\//, "").split('/')[0]}...{page.split('/').pop()?.slice(0, 10)}
                      <X 
                        className="w-3 h-3 ml-1.5 cursor-pointer hover:text-red-500" 
                        onClick={() => setSelectedPages(selectedPages.filter(p => p !== page))}
                      />
                    </span>
                  ))}
                  {selectedPages.length > 5 && (
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-500">
                      +{selectedPages.length - 5} more
                    </span>
                  )}
                </div>
              )}

              <div className="flex flex-col items-center gap-4 border-t pt-6 mt-6">
                <Button 
                  onClick={() => { setIsDropdownOpen(false); runAudit(); }}
                  disabled={isAuditing || selectedPages.length === 0} 
                  size="lg" 
                  className="w-full max-w-md bg-green-600 hover:bg-green-700 h-12 font-bold text-lg shadow-sm"
                >
                  {isAuditing ? (
                    <span className="flex items-center gap-2">
                      <Rocket className="w-5 h-5 animate-spin" />
                      Auditing... {Math.round(auditProgress)}%
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      <Rocket className="w-5 h-5" />
                      Run Deep Audit ({selectedPages.length})
                    </span>
                  )}
                </Button>
                {isAuditing && <Progress value={auditProgress} className="w-full max-w-md h-2" />}
              </div>
            </CardContent>
          </Card>
        )}
        {/* 4. Audit Results */}
        {Object.keys(auditResults).length > 0 && (
          <Card className="border-slate-200 shadow-xl overflow-hidden">
            <CardHeader className="bg-slate-900 text-white pb-6">
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle className="text-xl">3. Audit Report</CardTitle>
                  <CardDescription className="text-slate-400">AI-generated fixes and compliance scoring</CardDescription>
                </div>
                <Button variant="outline" size="sm" className="text-black border-white/20 hover:bg-white/10 hover:text-white transition-colors">
                  <Download className="w-4 h-4 mr-2" /> Export PDF
                </Button>
              </div>
            </CardHeader>
            
            <CardContent className="p-0">
              <Tabs defaultValue={Object.keys(auditResults)[0]} className="w-full">
                
                {/* Tab Bar */}
                <div className="bg-slate-100 border-b px-6 py-3 overflow-x-auto">
                  <TabsList className="bg-white p-1 h-auto inline-flex gap-2 rounded-lg border shadow-sm">
                    {Object.keys(auditResults).map((url) => (
                      <TabsTrigger 
                        key={url} 
                        value={url}
                        className="data-[state=active]:bg-blue-600 data-[state=active]:text-white px-4 py-2 text-sm"
                      >
                        {url.replace(/^https?:\/\//, "").split("/")[0]}...
                      </TabsTrigger>
                    ))}
                  </TabsList>
                </div>

                {/* Tab Content */}
                {Object.entries(auditResults).map(([url, data]) => {
                  const report = data.report || [];
                  const summary = data.summary || { total: 0, critical: 0, serious: 0, minor: 0, india_compliance: "N/A", status: "Unknown" };
                  
                  // Filter Logic
                  const filteredReport = report.filter((issue) => 
                    JSON.stringify(issue).toLowerCase().includes(searchTerm.toLowerCase())
                  );

                  return (
                    <TabsContent key={url} value={url} className="p-6 space-y-8 animate-in fade-in duration-300">
                      
                      {/* A. Metric Cards */}
                      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
                        <MetricCard label="Total Issues" value={summary.total} icon={<AlertCircle />} />
                        <MetricCard label="Critical" value={summary.critical} color="text-red-600" bg="bg-red-50" icon={<AlertTriangle />} />
                        <MetricCard label="Serious" value={summary.serious} color="text-orange-600" bg="bg-orange-50" icon={<AlertTriangle />} />
                        <MetricCard label="Indian Law" value={summary.india_compliance} 
                          color={summary.india_compliance === "PASS" ? "text-green-700" : "text-red-700"} 
                          bg={summary.india_compliance === "PASS" ? "bg-green-50" : "bg-red-50"}
                          isText
                        />
                        <div className={`p-4 rounded-xl border shadow-sm flex flex-col justify-center items-center text-center ${
                          summary.status === "Compliant" ? "bg-green-50 border-green-200" : "bg-slate-50 border-slate-200"
                        }`}>
                          <span className="text-xs text-slate-500 uppercase font-bold">Status</span>
                          <span className={`text-lg font-bold ${summary.status === "Compliant" ? "text-green-700" : "text-slate-900"}`}>
                            {summary.status}
                          </span>
                        </div>
                      </div>

                      {/* B. Violation Overview Table */}
                      {report.length > 0 && (
                        <div className="rounded-lg border border-slate-200 overflow-hidden">
                          <div className="bg-slate-50 px-4 py-3 border-b border-slate-200 font-semibold text-slate-700 flex justify-between items-center">
                            <span>📊 Violation Overview</span>
                            <div className="relative w-64">
                                <Search className="absolute left-2 top-2.5 h-4 w-4 text-gray-400" />
                                <Input 
                                  placeholder="Search issues..." 
                                  className="pl-8 h-9 bg-white"
                                  value={searchTerm}
                                  onChange={(e) => setSearchTerm(e.target.value)}
                                />
                            </div>
                          </div>
                          <table className="w-full text-sm text-left">
                            <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b">
                              <tr>
                                <th className="px-4 py-3">Priority</th>
                                <th className="px-4 py-3">Rule</th>
                                <th className="px-4 py-3">Description</th>
                                <th className="px-4 py-3">WCAG</th>
                                <th className="px-4 py-3">Source</th>
                              </tr>
                            </thead>
                            <tbody>
                              {filteredReport.slice(0, 10).map((issue, idx) => (
                                <tr key={idx} className="bg-white border-b hover:bg-slate-50 transition-colors">
                                  <td className="px-4 py-3 font-medium">
                                    <PriorityBadge priority={issue.fix_priority} />
                                  </td>
                                  <td className="px-4 py-3 font-mono text-slate-600">{issue.rule}</td>
                                  <td className="px-4 py-3 text-slate-700">{issue.description}</td>
                                  <td className="px-4 py-3 text-slate-500">{issue.wcag_sc}</td>
                                  <td className="px-4 py-3">
                                    {issue.is_vision ? <Badge variant="outline" className="border-purple-200 text-purple-700 bg-purple-50">Vision AI</Badge> : <Badge variant="outline" className="text-slate-500">Code</Badge>}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                          {filteredReport.length > 10 && (
                            <div className="px-4 py-2 text-xs text-center text-slate-500 bg-slate-50">
                              Showing top 10 of {filteredReport.length} issues
                            </div>
                          )}
                        </div>
                      )}

                      {/* C. Detailed Task List */}
                      <div className="space-y-4">
                        <div className="flex items-center gap-2">
                          <FileCode className="w-5 h-5 text-slate-700" />
                          <h3 className="text-lg font-bold text-slate-900">Developer Remediation Plan</h3>
                        </div>
                        
                        {filteredReport.length === 0 ? (
                          <div className="text-center py-12 bg-white rounded-xl border border-dashed">
                            <CheckCircle2 className="w-12 h-12 text-green-500 mx-auto mb-4" />
                            <h3 className="text-lg font-medium text-slate-900">No issues found!</h3>
                          </div>
                        ) : (
                          <Accordion type="single" collapsible className="w-full space-y-3">
                            {filteredReport.map((issue, idx) => {
                              const priority = issue.fix_priority || "LOW";
                              const isCritical = priority.includes("HIGH") || priority.includes("CRITICAL");
                              const isVision = issue.is_vision;

                              return (
                                <AccordionItem 
                                  key={idx} 
                                  value={`item-${idx}`} 
                                  className="bg-white border border-slate-200 rounded-lg px-0 overflow-hidden data-[state=open]:ring-1 data-[state=open]:ring-blue-500"
                                >
                                  <AccordionTrigger className="px-4 py-4 hover:bg-slate-50 hover:no-underline">
                                    <div className="flex items-center gap-4 text-left w-full">
                                      <PriorityBadge priority={priority} />
                                      
                                      <div className="flex-1">
                                        <div className="flex items-center gap-2">
                                          <span className="font-semibold text-slate-800">{issue.rule}</span>
                                          {isVision && <Eye className="w-4 h-4 text-purple-500" />}
                                        </div>
                                        <p className="text-sm text-slate-500 line-clamp-1">{issue.description}</p>
                                      </div>
                                    </div>
                                  </AccordionTrigger>
                                  
                                  <AccordionContent className="bg-slate-50/50 border-t px-6 py-6">
                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                                      {/* Left: The Problem */}
                                      <div className="space-y-4">
                                        <h4 className="text-sm font-bold text-slate-700 uppercase tracking-wider flex items-center gap-2">
                                          <AlertCircle className="w-4 h-4" /> The Violation
                                        </h4>
                                        <div className="bg-white p-4 rounded-lg border border-slate-200 space-y-3 text-sm">
                                          <div><span className="font-semibold text-slate-500">WCAG Criteria:</span> {issue.wcag_sc || "N/A"}</div>
                                          <div><span className="font-semibold text-slate-500">Selector:</span> <code className="bg-slate-100 px-1.5 py-0.5 rounded text-blue-700">{issue.selector?.slice(0, 60)}...</code></div>
                                          <div className="mt-2">
                                            <span className="font-semibold text-slate-500 block mb-1">Bad Code:</span>
                                            <pre className="bg-slate-900 text-slate-50 p-3 rounded-md overflow-x-auto text-xs font-mono">
                                              {issue.html_snippet || "Code not available (Visual Issue)"}
                                            </pre>
                                          </div>
                                        </div>
                                      </div>

                                      {/* Right: The Fix */}
                                      <div className="space-y-4">
                                        <h4 className="text-sm font-bold text-green-700 uppercase tracking-wider flex items-center gap-2">
                                          <Rocket className="w-4 h-4" /> AI Solution
                                        </h4>
                                        
                                        {issue.ai_explanation ? (
                                          <div className="space-y-3">
                                            <div className="bg-blue-50 p-3 rounded-md text-sm text-blue-900 border border-blue-100">
                                              {issue.ai_explanation}
                                            </div>
                                            <div className="relative">
                                              <div className="absolute top-0 right-0 bg-green-600 text-white text-[10px] px-2 py-1 rounded-bl-md rounded-tr-md font-bold">FIXED</div>
                                              <pre className="bg-green-50 p-4 rounded-md border border-green-200 text-xs overflow-x-auto text-green-900 font-mono">
                                                {issue.ai_fixed_code || "Manual fix required"}
                                              </pre>
                                            </div>
                                          </div>
                                        ) : (
                                          <div className="h-full flex items-center justify-center border-2 border-dashed border-slate-200 rounded-lg">
                                            <span className="text-slate-400 text-sm italic">AI fix pending...</span>
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  </AccordionContent>
                                </AccordionItem>
                              );
                            })}
                          </Accordion>
                        )}
                      </div>
                    </TabsContent>
                  );
                })}
              </Tabs>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}

// --- SUB COMPONENTS ---

function MetricCard({ label, value, color = "text-slate-900", bg = "bg-slate-100", icon, isText = false }: any) {
  return (
    <div className={`p-4 rounded-xl border shadow-sm flex items-center justify-between bg-white`}>
      <div>
        <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">{label}</p>
        <h3 className={`text-2xl font-extrabold ${color} mt-1`}>{value}</h3>
      </div>
      <div className={`p-2.5 ${bg} rounded-lg`}>
        {icon && <div className={`w-5 h-5 ${color}`}>{icon}</div>}
      </div>
    </div>
  );
}

function PriorityBadge({ priority }: { priority: string }) {
  if (priority.includes("CRITICAL") || priority.includes("HIGH")) {
    return <Badge className="bg-red-100 text-red-700 border-red-200 hover:bg-red-200">Critical</Badge>;
  }
  if (priority.includes("MEDIUM")) {
    return <Badge className="bg-orange-100 text-orange-700 border-orange-200 hover:bg-orange-200">Serious</Badge>;
  }
  return <Badge className="bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100">Minor</Badge>;
}