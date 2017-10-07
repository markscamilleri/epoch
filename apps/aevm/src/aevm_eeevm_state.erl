-module(aevm_eeevm_state).
%%%-------------------------------------------------------------------
%%% @author Happi (Erik Stenman)
%%% @copyright (C) 2017, Aeternity Anstalt
%%% @doc
%%%     Handle the machine state for the EEEVM.
%%% @end
%%% Created : 2 Oct 2017
%%%-------------------------------------------------------------------

-export([ accountbalance/2
	, address/1
	, call/1
        , caller/1
	, code/1
	, cp/1
	, data/1
	, extcode/4
	, extcodesize/2
	, gas/1
	, gasprice/1
	, init/1
	, init/2
	, jumpdests/1
	, origin/1
        , out/1
	, mem/1
	, number/1
	, set_call/2
	, set_code/2
	, set_cp/2
	, set_gas/2
	, set_jumpdests/2
	, set_mem/2
	, set_out/2
	, set_selfdestruct/2
	, set_stack/2
	, set_storage/2
	, stack/1
	, storage/1
	, trace_format/3
	, value/1
	]).

-include("aevm_eeevm.hrl").
 
init(Spec) -> init(Spec, #{}).

init(#{ env  := Env
      , exec := Exec
      , pre  := Pre} = _Spec, Opts) ->
    Address = maps:get(address, Exec),
    #{ address   => Address
     , caller    => maps:get(caller, Exec)
     , data      => maps:get(data, Exec)
     , gas       => maps:get(gas, Exec)
     , gas_price => maps:get(gasPrice, Exec)
     , origin    => maps:get(origin, Exec)
     , value     => maps:get(value, Exec)

     , number    => maps:get(currentNumber, Env)

     , balances  => get_balances(Pre)
     , ext_code_blocks => get_ext_code_blocks(Pre)
     , ext_code_sizes => get_ext_code_sizes(Pre)

     , out       => <<>>
     , call      => #{}

     , code      => maps:get(code, Exec)
     , cp        => 0
     , memory    => #{}
     , stack     => []
     , storage   => init_storage(Address, Pre)

     , do_trace  => maps:get(trace, Opts, false)
     , trace     => []
     , trace_fun => init_trace_fun(Opts)

     }.

init_storage(Address, #{} = Pre) ->
    case maps:get(Address, Pre, undefined) of
        undefined -> #{};
        #{storage := S} -> S
    end.

get_ext_code_sizes(#{} = Pre) ->
    maps:from_list(
      [{Address, byte_size(C)} || {Address, #{code := C}} <-maps:to_list(Pre)]).

get_ext_code_blocks(#{} = Pre) ->
    maps:from_list(
      [{Address, C} || {Address, #{code := C}} <-maps:to_list(Pre)]).

get_balances(#{} = Pre) ->
    maps:from_list(
      [{Address, B} || {Address, #{balance := B}}
			   <- maps:to_list(Pre)]).


init_trace_fun(Opts) ->
    maps:get(trace_fun, Opts, fun(S,A) -> io:format(S,A) end).

accountbalance(Address, State) ->
    maps:get(Address band ?MASK160, maps:get(balances, State), 0).
address(State)   -> maps:get(address, State).
call(State)      -> maps:get(call, State).
caller(State)    -> maps:get(caller, State).
cp(State)        -> maps:get(cp, State).
code(State)      -> maps:get(code, State).
data(State)      -> maps:get(data, State).
extcodesize(Adr, State) ->
    maps:get(Adr band ?MASK160, maps:get(ext_code_sizes, State), 0).
extcode(Account, Start, Length, State) ->
    CodeBlock = maps:get(Account band ?MASK160,
			 maps:get(ext_code_blocks, State), <<>>),
    aevm_eeevm_utils:bin_copy(Start, Length, CodeBlock).
    
jumpdests(State) -> maps:get(jumpdests, State).
stack(State)     -> maps:get(stack, State).
mem(State)       -> maps:get(memory, State).
number(State)    -> maps:get(number, State).
origin(State)    -> maps:get(origin, State).
out(State)       -> maps:get(out, State).
gas(State)       -> maps:get(gas, State).
gasprice(State)  -> maps:get(gas_price, State).
storage(State)   -> maps:get(storage, State).
value(State)     -> maps:get(value, State).

do_trace(State)  -> maps:get(do_trace, State).
trace(State)     -> maps:get(trace, State).
trace_fun(State) -> maps:get(trace_fun, State).


set_call(Value, State)    -> maps:put(call, Value, State).
set_cp(Value, State)      -> maps:put(cp, Value, State).
set_code(Value, State)    -> maps:put(code, Value, State).
set_stack(Value, State)   -> maps:put(stack, Value, State).
set_mem(Value, State)     -> maps:put(memory, Value, State).
set_out(Value, State)     -> maps:put(out, Value, State).
set_gas(Value, State)     -> maps:put(gas, Value, State).
set_storage(Value, State) -> maps:put(storage, Value, State).
set_jumpdests(Value, State)    -> maps:put(jumpdests, Value, State).
set_selfdestruct(Value, State) -> maps:put(selfdestruct, Value, State).

add_trace(T, State) ->
    Trace = trace(State),
    maps:put(trace, Trace ++ [T], State).

trace_format(String, Argument, State) ->
    CP   = aevm_eeevm_state:cp(State),
    Code = aevm_eeevm_state:code(State),
    OP   = aevm_eeevm:code_get_op(CP, Code),
    case do_trace(State) of
	true ->
	    F = trace_fun(State),
	    F("~8.16.0B : ~2.16.0B", [CP, OP]),
	    F(" ~w", [stack(State)]),
	    F(String, Argument),
	    add_trace({CP, OP}, State);
	false ->
	    State
    end.
