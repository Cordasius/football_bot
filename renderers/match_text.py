from models import Match, PlayerResponse


def format_player_name(player: PlayerResponse) -> str:
    if player.username:
        return f"@{player.username}"
    return player.first_name


def format_match_text(match: Match) -> str:
    base_text = (
        f"🏟 <b>Футбольный матч</b>\n\n"
        f"📍 Место: {match.field_name}\n"
        f"📅 Дата: {match.date}\n"
        f"⏰ Время: {match.time}\n"
        f"👥 Формат: {match.format_str}\n"
        f"🎯 Игроков нужно: {match.total_players_needed}\n"
    )

    if match.responses:
        going, maybe, not_going = match.get_player_count()
        waitlist = match.get_waitlist_count()
        main_players, reserve_players = match.get_main_and_reserve()

        players_text = (
            f"\n📊 <b>Статистика:</b>\n"
            f"✅ Идут: {going}/{match.total_players_needed}\n"
            f"🤔 Под вопросом: {maybe}\n"
            f"❌ Не идут: {not_going}\n"
        )

        if waitlist > 0:
            players_text += f"⏳ В резерве: {waitlist}\n"

        players_text += "\n<b>Состав:</b>\n"

        if main_players:
            players_text += "\n✅ <b>Идут:</b>\n"
            for i, player in enumerate(main_players, 1):
                players_text += f"{i}. {format_player_name(player)}\n"

        if reserve_players:
            players_text += "\n⏳ <b>Резерв:</b>\n"
            for i, player in enumerate(reserve_players, len(main_players) + 1):
                players_text += f"{i}. {format_player_name(player)}\n"

        maybe_players = match.get_maybe_players()
        if maybe_players:
            players_text += "\n🤔 <b>Под вопросом:</b>\n"
            for i, player in enumerate(maybe_players, 1):
                players_text += f"{i}. {format_player_name(player)}\n"

        not_going_players = match.get_not_going_players()
        if not_going_players:
            players_text += "\n❌ <b>Не идут:</b>\n"
            for i, player in enumerate(not_going_players, 1):
                players_text += f"{i}. {format_player_name(player)}\n"

        base_text += players_text

    base_text += "\n👇 Нажмите кнопку, чтобы отметить свое участие!"
    return base_text


def format_match_status(match: Match) -> str:
    going, maybe, not_going = match.get_player_count()
    waitlist = match.get_waitlist_count()
    main_players, reserve_players = match.get_main_and_reserve()

    text = (
        f"<b>Текущий статус матча:</b>\n\n"
        f"📍 Место: {match.field_name}\n"
        f"📅 Дата: {match.date}\n"
        f"⏰ Время: {match.time}\n"
        f"👥 Формат: {match.format_str}\n"
        f"🎯 Игроков нужно: {match.total_players_needed}\n\n"
        f"📊 <b>Статистика:</b>\n"
        f"✅ Идут: {going}/{match.total_players_needed}\n"
        f"🤔 Под вопросом: {maybe}\n"
        f"❌ Не идут: {not_going}\n"
    )

    if waitlist > 0:
        text += f"⏳ В резерве: {waitlist}\n"

    if match.responses:
        text += "\n<b>Состав:</b>\n"

        if main_players:
            text += "\n✅ <b>Идут:</b>\n"
            for i, player in enumerate(main_players, 1):
                text += f"{i}. {format_player_name(player)}\n"

        if reserve_players:
            text += "\n⏳ <b>Резерв:</b>\n"
            for i, player in enumerate(reserve_players, len(main_players) + 1):
                text += f"{i}. {format_player_name(player)}\n"

        maybe_players = match.get_maybe_players()
        if maybe_players:
            text += "\n🤔 <b>Под вопросом:</b>\n"
            for i, player in enumerate(maybe_players, 1):
                text += f"{i}. {format_player_name(player)}\n"

    return text
