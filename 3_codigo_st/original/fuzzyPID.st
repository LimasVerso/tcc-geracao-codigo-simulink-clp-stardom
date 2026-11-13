(*
 *
 * File: fuzzyPID.st
 *
 * IEC 61131-3 Structured Text (ST) code generated for subsystem "fuzzyPID/Fuzzy PID"
 *
 * Model name                      : fuzzyPID
 * Model version                   : 14.1
 * Model creator                   : The MathWorks, Inc.
 * Model last modified by          : The MathWorks, Inc.
 * Model last modified on          : Sun Nov 01 14:58:55 2026
 * Model sample time               : 0.1s
 * Subsystem name                  : fuzzyPID/Fuzzy PID
 * Subsystem sample time           : 0.1s
 * Simulink PLC Coder version      : 26.2 (R2026b) 22-May-2026
 * ST code generated on            : Thu Nov 12 17:19:31 2026
 *
 * Target IDE selection            : Generic
 * Test Bench included             : No
 *
 *)
FUNCTION_BLOCK Fuzzy0
VAR_INPUT
    ssMethodType: SINT;
    b_r: LREAL;
    y: LREAL;
END_VAR
VAR_OUTPUT
    u: LREAL;
END_VAR
VAR
    c_DiscreteTimeIntegrator_DS: LREAL;
    UD_DSTATE: LREAL;
    b: ARRAY [0..7] OF SINT := 1,1,2,2,1,2,1,2;
    b_b: ARRAY [0..3] OF SINT := 1,2,2,3;
END_VAR
VAR_TEMP
    inputMFCache: ARRAY [0..3] OF LREAL;
    rtb_TSamp: LREAL;
    rtb_defuzzifiedOutputs: LREAL;
    ruleID: DINT;
    c_rtb_TmpSignalConversionAt: LREAL;
    d_rtb_TmpSignalConversionAt: LREAL;
END_VAR
CASE ssMethodType OF
    0: 
        (* SystemInitialize for Atomic SubSystem: '<Root>/Fuzzy PID' *)
        (* InitializeConditions for DiscreteIntegrator: '<S1>/Discrete-Time Integrator' *)
        c_DiscreteTimeIntegrator_DS := 0.0;
        (* InitializeConditions for UnitDelay: '<S2>/UD'
         *
         * Block description for '<S2>/UD':
         *  
         *  Store in Global RAM *)
        UD_DSTATE := 0.0;
        (* End of SystemInitialize for SubSystem: '<Root>/Fuzzy PID' *)
    1: 
        (* Outputs for Atomic SubSystem: '<Root>/Fuzzy PID' *)
        (* SampleTimeMath: '<S2>/TSamp' incorporates:
         *  Gain: '<S1>/GE2'
         *
         * About '<S2>/TSamp':
         *  y = u * K where K = 1 / ( w * Ts )
         *   *)
        rtb_TSamp := ( -y) * 10.0;
        (* Outputs for Atomic SubSystem: '<S1>/Fuzzy Inference System' *)
        (* SignalConversion: '<S5>/TmpSignal ConversionAt SFunction Inport1' incorporates:
         *  Gain: '<S1>/GE'
         *  Gain: '<S1>/GE1'
         *  MATLAB Function: '<S3>/Evaluate Rule Antecedents'
         *  Sum: '<S1>/Sum1'
         *  Sum: '<S2>/Diff'
         *  UnitDelay: '<S2>/UD'
         *
         * Block description for '<S2>/Diff':
         *  
         *  Add in CPU
         *
         * Block description for '<S2>/UD':
         *  
         *  Store in Global RAM *)
        c_rtb_TmpSignalConversionAt := (b_r - y) * 10.0;
        d_rtb_TmpSignalConversionAt := (rtb_TSamp - UD_DSTATE) * 4.9829312090415572;
        (* MATLAB Function: '<S3>/Evaluate Rule Antecedents' *)
        (* MATLAB Function 'Evaluate Rule Antecedents': '<S5>:1' *)
        (* '<S5>:1:4' if SimulateUsing==1 && coder.internal.canUseExtrinsic ... *)
        (* '<S5>:1:5'         && (isa(inputs,'double') || isa(inputs,'single')) *)
        (* '<S5>:1:32' else *)
        (* '<S5>:1:33' if fis.inputFuzzySetType==1 *)
        (* '<S5>:1:34' [antecedentOutputs,sumAntecedentOutputs] = ... *)
        (* '<S5>:1:35'             fuzzy.internal.codegen.evaluateRuleAntecedent(... *)
        (* '<S5>:1:36'             inputs,fis,diagnostics); *)
        rtb_defuzzifiedOutputs := 0.0;
        inputMFCache[0] := EXP(( -((c_rtb_TmpSignalConversionAt - -10.0) * (c_rtb_TmpSignalConversionAt - -10.0))) / 98.0);
        inputMFCache[1] := EXP(( -((c_rtb_TmpSignalConversionAt - 10.0) * (c_rtb_TmpSignalConversionAt - 10.0))) / 98.0);
        inputMFCache[2] := EXP(( -((d_rtb_TmpSignalConversionAt - -10.0) * (d_rtb_TmpSignalConversionAt - -10.0))) / 98.0);
        inputMFCache[3] := EXP(( -((d_rtb_TmpSignalConversionAt - 10.0) * (d_rtb_TmpSignalConversionAt - 10.0))) / 98.0);
        (* MATLAB Function: '<S3>/Evaluate Rule Consequents' *)
        (* MATLAB Function 'Evaluate Rule Consequents': '<S6>:1' *)
        (* '<S6>:1:4' if SimulateUsing==1 && coder.internal.canUseExtrinsic ... *)
        (* '<S6>:1:5'         && (isa(inputs,'double') || isa(inputs,'single')) *)
        (* '<S6>:1:55' else *)
        (* '<S6>:1:56' if fis.inputFuzzySetType==1 *)
        (* '<S6>:1:57' if strcmp(char(fis.type),'mamdani') *)
        (* '<S6>:1:61' else *)
        (* '<S6>:1:62' aggregatedOutputs = ... *)
        (* '<S6>:1:63'                 fuzzy.internal.codegen.evaluateRuleConsequentForSugenoFIS(... *)
        (* '<S6>:1:64'                 inputs,antecedentOutputs,fis); *)
        c_rtb_TmpSignalConversionAt := 0.0;
        FOR ruleID := 0 TO 3 DO 
            (* MATLAB Function: '<S3>/Evaluate Rule Antecedents' *)
            d_rtb_TmpSignalConversionAt := inputMFCache[SINT_TO_DINT(b[ruleID + 4]) + 1] * inputMFCache[SINT_TO_DINT(b[ruleID]) - 1];
            rtb_defuzzifiedOutputs := rtb_defuzzifiedOutputs + d_rtb_TmpSignalConversionAt;
            (* MATLAB Function: '<S3>/Evaluate Rule Consequents' incorporates:
             *  MATLAB Function: '<S3>/Evaluate Rule Antecedents' *)
            c_rtb_TmpSignalConversionAt := ((((SINT_TO_LREAL(b_b[ruleID]) - 1.0) * 20.0) - 20.0) * d_rtb_TmpSignalConversionAt) + c_rtb_TmpSignalConversionAt;
        END_FOR;
        (* MATLAB Function: '<S3>/Defuzzify Outputs' incorporates:
         *  MATLAB Function: '<S3>/Evaluate Rule Antecedents' *)
        (* MATLAB Function 'Defuzzify Outputs': '<S4>:1' *)
        (* '<S4>:1:4' if SimulateUsing==1 && coder.internal.canUseExtrinsic ... *)
        (* '<S4>:1:5'         && (isa(aggregatedOutputs,'double') || isa(aggregatedOutputs,'single')) *)
        (* '<S4>:1:63' else *)
        (* '<S4>:1:64' if fis.inputFuzzySetType==1 *)
        (* '<S4>:1:65' if isequal(fis.type,uint8('mamdani')) *)
        (* '<S4>:1:70' else *)
        (* '<S4>:1:71' defuzzifiedOutputs = ... *)
        (* '<S4>:1:72'                 fuzzy.internal.codegen.applySugenoDefuzzificationMethod(... *)
        (* '<S4>:1:73'                 sumAntecedentOutputs,aggregatedOutputs,fis,diagnostics); *)
        IF rtb_defuzzifiedOutputs <> 0.0 THEN 
            rtb_defuzzifiedOutputs := (1.0 / rtb_defuzzifiedOutputs) * c_rtb_TmpSignalConversionAt;
        END_IF;
        (* End of MATLAB Function: '<S3>/Defuzzify Outputs' *)
        (* End of Outputs for SubSystem: '<S1>/Fuzzy Inference System' *)
        
        (* Outport: '<Root>/u' incorporates:
         *  DiscreteIntegrator: '<S1>/Discrete-Time Integrator'
         *  Gain: '<S1>/GE4'
         *  Gain: '<S1>/GE5'
         *  Gain: '<S1>/GE6'
         *  Sum: '<S1>/Sum2' *)
        u := (((4.9829312090415572 * b_r) * 2.5178914786420625) + c_DiscreteTimeIntegrator_DS) + (1.8102990617789958 * rtb_defuzzifiedOutputs);
        (* Update for DiscreteIntegrator: '<S1>/Discrete-Time Integrator' incorporates:
         *  Gain: '<S1>/GE3' *)
        c_DiscreteTimeIntegrator_DS := ((2.5178914786420625 * rtb_defuzzifiedOutputs) * 0.1) + c_DiscreteTimeIntegrator_DS;
        (* Update for UnitDelay: '<S2>/UD'
         *
         * Block description for '<S2>/UD':
         *  
         *  Store in Global RAM *)
        UD_DSTATE := rtb_TSamp;
        (* End of Outputs for SubSystem: '<Root>/Fuzzy PID' *)
END_CASE;
END_FUNCTION_BLOCK
