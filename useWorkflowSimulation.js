import { useState, useEffect, useRef } from 'react';
import { initialAgents } from '../mockData';

export function useWorkflowSimulation() {
  const isProcessingRef = useRef(false);
  const statsRef = useRef({ total: 0, pdf: 0, excel: 0, csv: 0, docx: 0, rejected: 0 });
  const [isProcessing, setIsProcessing] = useState(false);
  const [agents, setAgents] = useState(initialAgents);
  const [logs, setLogs] = useState([]);
  const [isComplete, setIsComplete] = useState(false);
  
  const [stepIndex, setStepIndex] = useState(0);
  const [simSteps, setSimSteps] = useState([]);
  const [isWaitingForBackend, setIsWaitingForBackend] = useState(false);
  const [backendFinished, setBackendFinished] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Generate sequence of steps
  const buildSteps = (stats) => {
    const steps = [];
    const addStep = (agent, action, output) => {
      steps.push({ agent, action, output });
    };

    const { total = 0, pdf = 0, excel = 0, csv = 0, docx = 0, rejected = 0 } = stats || {};
    const validFiles = Math.max(1, total - rejected);
    const pdfStreamFiles = pdf + docx;
    const excelStreamFiles = excel + csv;

    const pdfPages = pdfStreamFiles > 0 ? (pdfStreamFiles * 16) : 0; 
    const excelTables = excelStreamFiles > 0 ? (excelStreamFiles * 4) : 0;

    // 1. Intake
    addStep('intake', 'running', '-');
    addStep('intake', 'completed', `${total || 1} Files`);
    
    // 2. Detection
    addStep('detection', 'running', '-');
    addStep('detection', 'completed', `${validFiles} Valid`);
    
    // 3. Router
    addStep('router', 'running', '-');
    addStep('router', 'completed', `${pdfStreamFiles} PDF/DOC, ${excelStreamFiles} XLS`);
    
    // 4. File-specific routes
    if (docx > 0) {
      addStep('docToPdf', 'running', '-');
      addStep('docToPdf', 'completed', `${docx} PDF files`);
    }
    
    if (pdf > 0 || docx > 0) {
      addStep('pdfToImage', 'running', '-');
      addStep('pdfToImage', 'completed', `${pdfPages} Images`);
      addStep('imageToText', 'running', '-');
      addStep('imageToText', 'completed', `Extracted Text`);
    }

    if (excel > 0 || csv > 0 || (pdf === 0 && docx === 0)) {
      addStep('excelBlock', 'running', '-');
      addStep('excelBlock', 'completed', `${excelTables || 4} Tables`);
      addStep('excelText', 'running', '-');
      addStep('excelText', 'completed', `Parsed JSON`);
    }
    
    // 5. Final Extract PAUSE POINT
    addStep('finalExtract', 'running', 'Pending backend...');

    return steps;
  };

  // Timer Effect
  useEffect(() => {
    let timerId;
    if (isWaitingForBackend) {
      timerId = setInterval(() => {
        setElapsedTime(prev => {
          const next = prev + 1;
          setAgents(currAgents => currAgents.map(a => {
            if (a.id === 'finalExtract' && a.status === 'running') {
              return { ...a, time: `${next.toFixed(1)}s` };
            }
            return a;
          }));
          return next;
        });
      }, 1000);
    }
    return () => clearInterval(timerId);
  }, [isWaitingForBackend]);

  // Visual Progression Effect
  useEffect(() => {
    if (!isProcessing || isWaitingForBackend) return;

    if (stepIndex < simSteps.length) {
      const timerId = setTimeout(() => {
        // Abort if processing was cancelled or completed early (e.g. fast API response)
        if (!isProcessingRef.current) return;

        const step = simSteps[stepIndex];
        
        // Apply step state
        setAgents(prev => prev.map(a => 
          a.id === step.agent ? { ...a, status: step.action, output: step.output } : a
        ));

        // Check if this is the pause point
        if (step.agent === 'finalExtract' && step.action === 'running') {
          if (!backendFinished) {
             setIsWaitingForBackend(true);
          }
        }

        setStepIndex(prev => prev + 1);
        
        // If it's the very last step and we are NOT waiting for backend
        if (stepIndex === simSteps.length - 1 && step.agent !== 'finalExtract') {
          setIsComplete(true);
          setIsProcessing(false);
          setLogs(prev => [...prev, {
            id: Math.random().toString(), time: new Date().toLocaleTimeString([], { hour12: false }), text: 'Pipeline completed successfully.', type: 'info'
          }]);
        }
      }, 600); // 600ms per visual step
      return () => clearTimeout(timerId);
    }
  }, [isProcessing, isWaitingForBackend, stepIndex, simSteps, backendFinished]);

  const startSimulation = (stats) => {
    statsRef.current = stats || { total: 1, pdf: 0, excel: 1, csv: 0, docx: 0, rejected: 0 };
    isProcessingRef.current = true;
    setIsProcessing(true);
    setIsComplete(false);
    setBackendFinished(false);
    setIsWaitingForBackend(false);
    setStepIndex(0);
    setElapsedTime(0);
    setSimSteps(buildSteps(stats));
    setAgents(initialAgents);
    setLogs([
      { id: '1', time: new Date().toLocaleTimeString([], { hour12: false }), text: 'Starting pipeline execution...', type: 'info' }
    ]);
  };

  const completeSimulation = (result) => {
    // Try to find actual claims extracted from result
    let claimsCount = 0;
    let filesCount = statsRef.current.total || 1;
    let validFilesCount = Math.max(1, filesCount - (statsRef.current.rejected || 0));
    try {
      if (result && result.claimsExtracted !== undefined) {
        claimsCount = result.claimsExtracted;
      }
      if (result && result.filesUploaded !== undefined) {
        filesCount = result.filesUploaded;
      }
      if (result && result.validLossRuns !== undefined) {
        validFilesCount = result.validLossRuns;
      }
    } catch (e) {}

    const stats = statsRef.current;
    const hasExcel = (stats.excel > 0 || stats.csv > 0) || (filesCount > 0 && stats.pdf === 0 && stats.docx === 0);
    const hasPdf = (stats.pdf > 0);
    const hasDoc = (stats.docx > 0);

    // Clear any pending step timers
    isProcessingRef.current = false;
    setBackendFinished(true);
    setIsWaitingForBackend(false); 
    setIsComplete(true);
    setIsProcessing(false);

    // Update all agents cleanly based on stats & backend response
    setAgents(currAgents => currAgents.map(a => {
      // 1. Universal Intake & Detection Stages (Always Completed)
      if (a.id === 'intake') {
        return { ...a, status: 'completed', output: `${filesCount} Files Ingested` };
      }
      if (a.id === 'detection') {
        return { ...a, status: 'completed', output: `${validFilesCount} Valid Loss Runs` };
      }
      if (a.id === 'router') {
        const streamText = hasExcel ? `${filesCount} Excel/CSV` : `${filesCount} PDF/DOC`;
        return { ...a, status: 'completed', output: `Routed ${streamText}` };
      }

      // 2. Excel / Tabular Stream
      if (a.id === 'excelBlock') {
        return hasExcel 
          ? { ...a, status: 'completed', output: `Block Matrix Detected` }
          : { ...a, status: 'idle', output: 'Bypassed (No Excel/CSV)' };
      }
      if (a.id === 'excelText') {
        return hasExcel 
          ? { ...a, status: 'completed', output: 'Tabular Records Extracted' }
          : { ...a, status: 'idle', output: 'Bypassed (No Excel/CSV)' };
      }

      // 3. PDF / Document Stream
      if (a.id === 'docToPdf') {
        return hasDoc 
          ? { ...a, status: 'completed', output: `${stats.docx} Converted to PDF` }
          : { ...a, status: 'idle', output: 'Bypassed (No DOCX)' };
      }
      if (a.id === 'pdfToImage') {
        return (hasPdf || hasDoc)
          ? { ...a, status: 'completed', output: 'Rendered Page Streams' }
          : { ...a, status: 'idle', output: 'Bypassed (No PDF/DOC)' };
      }
      if (a.id === 'imageToText') {
        return (hasPdf || hasDoc)
          ? { ...a, status: 'completed', output: 'Digital Stream / OCR Extracted' }
          : { ...a, status: 'idle', output: 'Bypassed (No PDF/DOC)' };
      }

      // 4. Downstream Pipeline Stages (Always Completed on success)
      if (a.id === 'finalExtract') {
        return { ...a, status: 'completed', output: `${claimsCount} Claims Extracted` };
      }
      if (a.id === 'transform') {
        return { ...a, status: 'completed', output: 'Schema Standardized' };
      }
      if (a.id === 'validation') {
        return { ...a, status: 'completed', output: 'Business Validated' };
      }
      if (a.id === 'rollup') {
        return { ...a, status: 'completed', output: 'Occurrences Bundled' };
      }
      if (a.id === 'report') {
        return { ...a, status: 'completed', output: 'Master Package Ready' };
      }

      return { ...a, status: 'completed', output: 'Completed' };
    }));
    
    setLogs(prev => [...prev, {
      id: Math.random().toString(), time: new Date().toLocaleTimeString([], { hour12: false }), text: `Backend returned payload with ${claimsCount} claims. Finalizing UI...`, type: 'info'
    }, {
      id: Math.random().toString(), time: new Date().toLocaleTimeString([], { hour12: false }), text: 'Pipeline completed successfully.', type: 'info'
    }]);
  };

  const failSimulation = (errorMsg) => {
    isProcessingRef.current = false;
    setIsProcessing(false);
    setIsWaitingForBackend(false);
    setAgents(prev => prev.map(a => {
      if (a.status === 'running') {
        return { ...a, status: 'failed', output: 'Failed' };
      }
      return a;
    }));
    setLogs(prev => [...prev, {
      id: Math.random().toString(), time: new Date().toLocaleTimeString([], { hour12: false }), text: `Pipeline failed: ${errorMsg}`, type: 'warning'
    }]);
  };

  const restart = () => {
    isProcessingRef.current = false;
    setIsProcessing(false);
    setAgents(initialAgents);
    setLogs([]);
    setIsComplete(false);
    setElapsedTime(0);
    setStepIndex(0);
    setBackendFinished(false);
    setIsWaitingForBackend(false);
  };

  return { isProcessing, isComplete, agents, logs, startSimulation, completeSimulation, failSimulation, restart, setAgents };
}
