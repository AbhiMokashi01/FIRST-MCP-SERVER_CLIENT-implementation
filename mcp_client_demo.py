from mcp import Client
import asyncio



async def main():
    print("inside main")
    async with Client("http://127.0.0.1:8000/mcp") as client:
        tools_list=await client.list_tools()
        # tool_count=1
        # for tool in tools_list.tools:
        #     print(f"tool no :{tool_count}")
        #     print(tool.name)
        #     print(tool.description)
        #     print(tool.input_schema)
        #     tool_count+=1

        await client.call_tool("save_note_tool",{"topic":"Math","content":"NICE BRAIN"})
        await client.call_tool("search_notes_tool",{"keyword":"ABHISHEK"})
        print(await client.call_tool("calculate_percentage",{"total":99,"percentage":"80"}))
        print(await client.read_resource("study://guide/python"))
        print(await client.get_prompt("explain_topic",{"topic":"python"}))
        
    

if __name__=="__main__":
    asyncio.run(main())


# client=MultiServerMCPClient(
#     {
#         "study_assistant_server": {
#             "url":"http://127.0.0.1:8000",
#             "transport":"streamable-http"
#         }
#     }
# )


