
import asyncio
from telethon import TelegramClient, functions, types
from telethon.errors import FloodWaitError

# Enter your Telegram API credentials
API_ID = 30489872
API_HASH = "c0518472961df479c4403b6a7eab2db6"

SESSION_NAME = "telegram_session"


async def main():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    await client.start()

    print("\nConnected to Telegram successfully!")

    targets = []

    print("\nFetching your groups and channels...")

    async for dialog in client.iter_dialogs():
        entity = dialog.entity

        if isinstance(entity, (types.Chat, types.Channel)):
            targets.append(dialog)

    print(f"\nTotal groups and channels found: {len(targets)}")

    if not targets:
        print("Nothing to leave.")
        await client.disconnect()
        return

    print("\nGroups and channels:")
    for index, dialog in enumerate(targets, 1):
        print(f"{index}. {dialog.name}")

    print("\nWARNING: This action cannot be automatically undone.")
    confirm = input(
        "\nType LEAVE ALL to confirm: "
    )

    if confirm != "LEAVE ALL":
        print("Cancelled. Nothing changed.")
        await client.disconnect()
        return

    success = 0
    failed = 0

    print("\nStarting cleanup...\n")

    for dialog in targets:
        entity = dialog.entity

        try:
            if isinstance(entity, types.Channel):
                await client(
                    functions.channels.LeaveChannelRequest(
                        channel=entity
                    )
                )

            elif isinstance(entity, types.Chat):
                await client(
                    functions.messages.DeleteChatUserRequest(
                        chat_id=entity.id,
                        user_id="me"
                    )
                )

            success += 1
            print(f"[LEFT] {dialog.name}")

            await asyncio.sleep(2)

        except FloodWaitError as error:
            print(
                f"[WAIT] Telegram requested "
                f"{error.seconds} seconds. Waiting..."
            )
            await asyncio.sleep(error.seconds + 1)

            try:
                if isinstance(entity, types.Channel):
                    await client(
                        functions.channels.LeaveChannelRequest(
                            channel=entity
                        )
                    )
                else:
                    await client(
                        functions.messages.DeleteChatUserRequest(
                            chat_id=entity.id,
                            user_id="me"
                        )
                    )

                success += 1
                print(f"[LEFT] {dialog.name}")

            except Exception as retry_error:
                failed += 1
                print(f"[FAILED] {dialog.name}: {retry_error}")

        except Exception as error:
            failed += 1
            print(f"[FAILED] {dialog.name}: {error}")

    print("\n========== SUMMARY ==========")
    print(f"Successfully left: {success}")
    print(f"Failed: {failed}")
    print("==============================")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())



