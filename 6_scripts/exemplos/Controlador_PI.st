(*
 *
 * File: Controlador_PI.st
 *
 * IEC 61131-3 Structured Text (ST) code generated for subsystem "Controlador_PI/Controlador"
 *
 * Model name                      : Controlador_PI
 * Model version                   : 2.4
 * Model creator                   : joaov
 * Model last modified by          : João
 * Model last modified on          : Tue Oct 27 14:32:09 2026
 * Model sample time               : 0.1s
 * Subsystem name                  : Controlador_PI/Controlador
 * Subsystem sample time           : 0.1s
 * Simulink PLC Coder version      : 26.2 (R2026b) 22-May-2026
 * ST code generated on            : Tue Nov 03 20:40:08 2026
 *
 * Target IDE selection            : Generic
 * Test Bench included             : No
 *
 *)
FUNCTION_BLOCK Controlador
VAR_INPUT
    ssMethodType: SINT;
    In1: LREAL;
    In2: LREAL;
END_VAR
VAR_OUTPUT
    Out1: LREAL;
END_VAR
VAR
    c_DiscreteTimeIntegrator_DS: LREAL;
END_VAR
VAR_TEMP
    rtb_Sum: LREAL;
END_VAR
CASE ssMethodType OF
    0: 
        (* SystemInitialize for Atomic SubSystem: '<Root>/Controlador' *)
        (* InitializeConditions for DiscreteIntegrator: '<S1>/Discrete-Time Integrator' *)
        c_DiscreteTimeIntegrator_DS := 0.0;
        (* End of SystemInitialize for SubSystem: '<Root>/Controlador' *)
    1: 
        (* Outputs for Atomic SubSystem: '<Root>/Controlador' *)
        (* Sum: '<S1>/Sum' *)
        rtb_Sum := In1 - In2;
        (* Outport: '<Root>/Out1' incorporates:
         *  DiscreteIntegrator: '<S1>/Discrete-Time Integrator'
         *  Gain: '<S1>/Ganho proporcional'
         *  Sum: '<S1>/Sum1' *)
        Out1 := (1.1 * rtb_Sum) + c_DiscreteTimeIntegrator_DS;
        (* Update for DiscreteIntegrator: '<S1>/Discrete-Time Integrator' incorporates:
         *  Gain: '<S1>/Ganho integral' *)
        c_DiscreteTimeIntegrator_DS := ((1.83 * rtb_Sum) * 0.1) + c_DiscreteTimeIntegrator_DS;
        (* End of Outputs for SubSystem: '<Root>/Controlador' *)
END_CASE;
END_FUNCTION_BLOCK
