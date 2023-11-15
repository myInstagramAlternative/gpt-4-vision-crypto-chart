import ast
import time
from openai import OpenAI, types as openai_types
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient


class CryptoTraderGpt:
    def __init__(self, openai_key=None, binance_api_key=None, binance_api_secret=None):
        self.client = OpenAI(api_key=openai_key)
        self.binance_client = SpotWebsocketStreamClient(
            api_key=binance_api_key,
            api_secret=binance_api_secret,
        )
        self.thread_id = "thread_oC4pxyFeMuDuP2OmHAntg92y"
        self.function_map = {
            "get_token_price": self.get_token_price,
        }

    def _list_thread_runs(self):
        thread_runs = self.client.beta.threads.runs.list(
            thread_id=self.thread_id,
        )
        return thread_runs

    def _get_last_thread_run(self):
        return self._list_thread_runs().data[0]

    def check_required_action(self):
        last_thread_run = self._get_last_thread_run()
        run_id = last_thread_run.id
        if last_thread_run.required_action != None:
            required_action = last_thread_run.required_action
            if required_action.submit_tool_outputs != None:
                # print(required_action.submit_tool_outputs)
                tool_outputs = []
                for tool_call in required_action.submit_tool_outputs.tool_calls:
                    if tool_call.type == "function":
                        tool_call_id = tool_call.id
                        response = self.function_handler(tool_call.function)
                        tool_outputs.append(
                            openai_types.beta.threads.run_submit_tool_outputs_params.ToolOutput(
                                output=response, tool_call_id=tool_call_id
                            )
                        )

                self.submit_tool_outputs(run_id, tool_outputs)
                # print(required_action.submit_tool_outputs)
                # tool_call_id = required_action.submit_tool_outputs.
                # function_name = required_action.submit_tool_outputs.function_name
                # function_arguments = required_action.submit_tool_outputs.function_arguments
                # return tool_call_id, function_name, function_arguments
        return None

    def submit_tool_outputs(self, run_id, tool_outputs):
        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread_id,
            run_id=run_id,
            tool_outputs=tool_outputs,
        )

    def function_handler(self, function):
        if function.name in self.function_map:
            print(function.arguments)
            return self.function_map[function.name](
                **ast.literal_eval(function.arguments)
            )

    def get_token_price(self, symbol, exchange="binance"):
        avg_price = self.binance_client.avg_price(symbol="BTCUSDT")
        print(avg_price)
        return avg_price

    def test(self):
        return self.check_required_action()

def message_handler(_, message):
    print(message)

binance_client = SpotWebsocketStreamClient(
            on_message=message_handler,
        )


avg_price = binance_client.ticker(symbol="BTCUSDT")
print(avg_price)
time.sleep(5)
binance_client.ticker(action=SpotWebsocketStreamClient.ACTION_UNSUBSCRIBE)