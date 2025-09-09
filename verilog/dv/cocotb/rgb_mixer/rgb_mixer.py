from caravel_cocotb.caravel_interfaces import * # import python APIs
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles, with_timeout
import sys
sys.path.append("../../../rgb_mixer") 
from encoder import Encoder

clocks_per_phase = 10

async def run_encoder_test(encoder, dut_enc, max_count):
    for i in range(clocks_per_phase * 2 * max_count):
        await encoder.update(1)

    # let noisy transition finish, otherwise can get an extra count
    for i in range(10):
        await encoder.update(0)
    
    # when we have the internal signals (not GL) can also assert the values
    if dut_enc is not None:
        assert(dut_enc == max_count)

@cocotb.test() # cocotb test marker
@report_test # wrapper for configure test reporting files
async def rgb_mixer(dut):
    caravelEnv = await test_configure(dut) #configure, start up and reset caravel
    
    # enable the outputs
    dut.gpio8_en.value = 1
    dut.gpio9_en.value = 1
    dut.gpio10_en.value = 1
    dut.gpio11_en.value = 1
    dut.gpio12_en.value = 1
    dut.gpio13_en.value = 1

    # setup encoders
    encoder0 = Encoder(caravelEnv.clk, dut.gpio8, dut.gpio9, clocks_per_phase = clocks_per_phase, noise_cycles = clocks_per_phase / 4)
    encoder1 = Encoder(caravelEnv.clk, dut.gpio10, dut.gpio11, clocks_per_phase = clocks_per_phase, noise_cycles = clocks_per_phase / 4)
    encoder2 = Encoder(caravelEnv.clk, dut.gpio12, dut.gpio13, clocks_per_phase = clocks_per_phase, noise_cycles = clocks_per_phase / 4)

    cocotb.log.info (f"waiting for the design to be ready")
    # wait for the reset signal - time out if necessary - should happen around 165us
    await with_timeout(RisingEdge (dut.gpio17_monitor), 5, 'ms')
    await with_timeout(FallingEdge(dut.gpio17_monitor), 1, 'ms')

    # pwm should all be low at start
    # monitor lets us read the value
    assert dut.gpio14_monitor.value == 0
    assert dut.gpio15_monitor.value == 0
    assert dut.gpio16_monitor.value == 0
    cocotb.log.info (f"pwm all 0")

    # do 3 ramps for each encoder 
    max_count = 255
    await run_encoder_test(encoder0, None, max_count)
    await run_encoder_test(encoder1, None, max_count)
    await run_encoder_test(encoder2, None, max_count)

    # sync to pwm
    cocotb.log.info (f"waiting to sync on positive edge of 1st PWM output")
    await with_timeout(RisingEdge(dut.gpio14_monitor), 1, 'ms')

    # pwm should all be on for max_count 
    for i in range(max_count): 
        assert dut.gpio14_monitor.value == 1
        assert dut.gpio15_monitor.value == 1
        assert dut.gpio16_monitor.value == 1
        await ClockCycles(caravelEnv.clk, 1)
