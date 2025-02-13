import pytz
from django.db.models import Q
from django.db import transaction

import alerts.util
import general.cloudinary
import scouting
import scouting.util
from general.security import ret_message
from scouting.models import (
    Event,
    Team,
    TeamNote,
    MatchStrategy,
    AllianceSelection,
    FieldResponse,
    Dashboard,
    DashboardGraph,
)
from scouting.strategizing.serializers import (
    HistogramSerializer,
    PlotSerializer,
    BoxAndWhiskerPlotSerializer,
    HistogramBinSerializer,
    HeatmapSerializer,
)
from user.models import User
import form.util
import form.models


def get_team_notes(team_no: int = None, event: Event = None):
    q_event = Q()
    q_team = Q()

    if team_no is not None:
        q_team = Q(team_no=Team.objects.get(Q(void_ind="n") & Q(team_no=team_no)))

    if event is not None:
        q_event = Q(event=event)

    notes = TeamNote.objects.filter(Q(void_ind="n") & q_team & q_event).order_by(
        "-time"
    )

    return [parse_team_note(n) for n in notes]


def parse_team_note(n: TeamNote):
    return {
        "id": n.id,
        "team_id": n.team.team_no,
        "match_id": n.match.match_key if n.match else None,
        "note": n.note,
        "time": n.time,
        "user": n.user,
    }


def save_note(data, user: User):
    current_event = scouting.util.get_current_event()

    note = TeamNote(
        event=current_event,
        team_id=data["team_id"],
        match_id=data.get("match_id", None),
        user=user,
        note=data["note"],
    )

    note.save()

    return ret_message("Note saved successfully")


def get_match_strategies(match_id: int = None, event: Event = None):
    q_match_id = Q()
    q_event = Q()

    if match_id is not None:
        q_match_id = Q(id=match_id)

    if event is not None:
        q_event = Q(match__event=event)

    match_strategies = (
        MatchStrategy.objects.prefetch_related(
            "match__event",
            "match__blue_one",
            "match__blue_two",
            "match__blue_three",
            "match__red_one",
            "match__red_two",
            "match__red_three",
            "match__fieldresponse_set",
            "match__blue_one__eventteaminfo_set",
            "match__blue_two__eventteaminfo_set",
            "match__blue_three__eventteaminfo_set",
            "match__red_one__eventteaminfo_set",
            "match__red_two__eventteaminfo_set",
            "match__red_three__eventteaminfo_set",
        )
        .filter(q_match_id & q_event & Q(void_ind="n"))
        .order_by("-time")
    )

    parsed_match_strategies = []
    for ms in match_strategies:
        parsed_match_strategies.append(
            {
                "id": ms.id,
                "match": scouting.util.parse_match(ms.match),
                "user": ms.user,
                "strategy": ms.strategy,
                "img_url": general.cloudinary.build_image_url(ms.img_id, ms.img_ver),
                "time": ms.time,
                "display_value": f"{ms.user.get_full_name()} {ms.time.astimezone(pytz.timezone('America/New_York' if event is None else event.timezone)).strftime('%m/%d/%Y, %I:%M%p')}",
            }
        )

    return parsed_match_strategies


def save_match_strategy(data, img=None):
    send_alert = False
    if data.get("id", None) is not None:
        match_strategy = MatchStrategy.objects.get(id=data["id"])
        send_alert = True
    else:
        match_strategy = MatchStrategy()

    match_strategy.match_id = data["match_key"]
    match_strategy.user_id = data["user_id"]
    match_strategy.strategy = data["strategy"]

    if img is not None:
        img = general.cloudinary.upload_image(img, match_strategy.img_id)

    if img is not None:
        match_strategy.img_id = img["public_id"]
        match_strategy.img_ver = img["version"]

    match_strategy.save()

    alerts.util.send_alerts_to_role(
        "Match Strategy Added",
        f"New match strategy from {match_strategy.user.get_full_name()} on match {match_strategy.match.match_number}",
        "match_strat_added",
        ["notification", "txt"],
        match_strategy.user.id,
    )


def get_alliance_selections():
    selections = AllianceSelection.objects.filter(
        Q(event=scouting.util.get_current_event()) & Q(void_ind="n")
    ).order_by("order")

    parsed = []
    for selection in selections:
        parsed.append(
            {
                "id": selection.id,
                "event": selection.event,
                "team": selection.team,
                "note": selection.note,
                "order": selection.order,
            }
        )

    return selections


def save_alliance_selections(data):
    for d in data:
        if d.get("id") is not None:
            selection = AllianceSelection.objects.get(id=d["id"])
        else:
            selection = AllianceSelection()

        selection.event_id = d["event"]["id"]
        selection.team_id = d["team"]["team_no"]
        selection.note = d["note"]
        selection.order = d["order"]

        selection.save()


def graph_team(graph: form.models.Graph, team_ids, reference_team_id=None):
    all_graphs = []
    for team_id in team_ids:
        responses = [
            resp.response
            for resp in FieldResponse.objects.filter(
                Q(team_id=team_id)
                & Q(void_ind="n")
                & Q(event=scouting.util.get_current_event())
            )
        ]
        aggregate_responses = None
        if reference_team_id is not None and reference_team_id != "null":
            aggregate_responses = [
                resp.response
                for resp in FieldResponse.objects.filter(
                    Q(team_id=reference_team_id)
                    & Q(void_ind="n")
                    & Q(event=scouting.util.get_current_event())
                )
            ]

        team_graph = form.util.graph_responses(graph.id, responses, aggregate_responses)

        if len(team_ids) <= 1:
            all_graphs = team_graph
        else:
            match graph.graph_typ.graph_typ:
                case "histogram":
                    for label in team_graph:
                        for g_bin in label["bins"]:
                            g_bin["bin"] = f"{team_id}: {g_bin['bin']}"

                            # merge graphs
                            if len(all_graphs) > 0:
                                for all_label in all_graphs:
                                    if all_label["label"] == label["label"]:
                                        all_label["bins"].append(g_bin)
                    # merge graphs
                    if len(all_graphs) <= 0:
                        all_graphs = team_graph

                case "ctg-hstgrm":
                    for label in team_graph:
                        for g_bin in label["bins"]:
                            g_bin["bin"] = f"{team_id}: {g_bin['bin']}"

                            # merge graphs
                            if len(all_graphs) > 0:
                                for all_label in all_graphs:
                                    if all_label["label"] == label["label"]:
                                        all_label["bins"].append(g_bin)
                    # merge graphs
                    if len(all_graphs) <= 0:
                        all_graphs = team_graph
                case "res-plot":
                    for label in team_graph:
                        label["label"] = f"{team_id}: {label['label']}"

                        all_graphs.append(label)
                case "diff-plot":
                    for label in team_graph:
                        label["label"] = f"{team_id}: {label['label']}"

                        all_graphs.append(label)
                case "box-wskr":
                    for plot in team_graph:
                        plot["label"] = f"{team_id}: {plot['label']}"

                        all_graphs.append(plot)
                case "ht-map":
                    for heatmap in team_graph:
                        heatmap["question"][
                            "question"
                        ] = f"{team_id}: {heatmap['question']['question']}"

                        all_graphs.append(heatmap)

    return all_graphs


def serialize_graph_team(graph_id, team_ids, reference_team_id=None):
    graph = form.models.Graph.objects.get(id=graph_id)

    data = graph_team(graph, team_ids, reference_team_id)

    serializer = None
    match graph.graph_typ.graph_typ:
        case "histogram":
            serializer = HistogramSerializer(data, many=True)
        case "ctg-hstgrm":
            # TODO how to handle single
            serializer = HistogramSerializer(data, many=True)
        case "res-plot":
            serializer = PlotSerializer(data, many=True)
        case "diff-plot":
            serializer = PlotSerializer(data, many=True)
        case "box-wskr":
            serializer = BoxAndWhiskerPlotSerializer(data, many=True)
        case "ht-map":
            serializer = HeatmapSerializer(data, many=True)

    return serializer.data


def get_dashboard(user_id):
    try:
        dashboard = Dashboard.objects.get(
            Q(user_id=user_id)
            & Q(season=scouting.util.get_current_season())
            & Q(void_ind="n")
            & Q(active="y")
        )
    except Dashboard.DoesNotExist:
        dashboard = Dashboard(
            user_id=user_id, season=scouting.util.get_current_season()
        )
        dashboard.save()

    parsed = {
        "id": dashboard.id,
        "active": dashboard.active,
        "teams": [
            scouting.util.parse_team(team, True) for team in dashboard.teams.all()
        ],
        "reference_team_id": dashboard.reference_team_id,
        "dashboard_graphs": [
            {
                "id": dashboard_graph.id,
                "graph_id": dashboard_graph.graph.id,
                "graph_name": dashboard_graph.graph.name,
                "graph_typ": dashboard_graph.graph.graph_typ.graph_typ,
                "graph_nm": dashboard_graph.graph.graph_typ.graph_nm,
                "x_scale_min": dashboard_graph.graph.x_scale_min,
                "x_scale_max": dashboard_graph.graph.x_scale_max,
                "y_scale_min": dashboard_graph.graph.y_scale_min,
                "y_scale_max": dashboard_graph.graph.y_scale_max,
                "order": dashboard_graph.order,
                "active": dashboard_graph.active,
            }
            for dashboard_graph in dashboard.dashboardgraph_set.filter(
                Q(active="y")
                & Q(void_ind="n")
                & Q(graph__active="y")
                & Q(graph__void_ind="n")
            ).order_by("order")
        ],
    }

    return parsed


def save_dashboard(data, user_id):
    with transaction.atomic():
        if data.get("id", None) is None:
            dashboard = Dashboard(user_id=user_id)
        else:
            dashboard = Dashboard.objects.get(id=data["id"])

        if dashboard.season is None:
            dashboard.season = scouting.util.get_current_season()

        dashboard.active = data["active"]

        dashboard.teams.set(
            Team.objects.filter(
                team_no__in=set(
                    team["team_no"] for team in data["teams"] if team["checked"]
                )
            )
        )
        dashboard.reference_team_id = data.get("reference_team_id", None)

        dashboard.save()

        for dashboard_graph_data in data.get("dashboard_graphs", []):
            if dashboard_graph_data.get("id", None) is None:
                try:
                    dashboard_graph = DashboardGraph.objects.get(
                        Q(dashboard=dashboard)
                        & Q(void_ind="n")
                        & Q(graph_id=dashboard_graph_data["graph_id"])
                    )
                except DashboardGraph.DoesNotExist:
                    dashboard_graph = DashboardGraph(dashboard=dashboard)
            else:
                dashboard_graph = DashboardGraph.objects.get(
                    id=dashboard_graph_data["id"]
                )

            dashboard_graph.graph_id = dashboard_graph_data["graph_id"]
            dashboard_graph.order = dashboard_graph_data["order"]
            dashboard_graph.active = dashboard_graph_data["active"]

            dashboard_graph.save()
