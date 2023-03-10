# Module: zycap
# File:   gen_modules.tcl
# Date:   08:35 12/10/2020
# Type:   None
# DO NOT MODIFY THIS FILE; AUTOMATICALLY GENERATED BY INTERFACER

####### Checkpoint for Module - fft #######

create_project -part xc7z020-clg400 -in_memory


read_verilog { rtl/static.v rtl/blink.v rtl/top_1.v rtl/test_ip_blackbox.v rtl/top.v } 

synth_design -top fft -mode out_of_context 
write_checkpoint rtl/.inst//fft.dcp

close_project

####### Checkpoint for Module - top_v1 #######

create_project -part xc7z020-clg400 -in_memory


read_verilog { rtl/static.v rtl/blink.v rtl/top_1.v rtl/test_ip_blackbox.v rtl/top.v } 

synth_design -top top_v1 -mode out_of_context 
write_checkpoint rtl/.inst//top_v1.dcp

close_project

