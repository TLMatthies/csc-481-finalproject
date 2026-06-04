%% clubs_kb.pl
%% Auto-generated from data/clubs.json — do not edit by hand.
%% Regenerate with:  python generate_kb.py
%%
%% Facts
%%   club/2            club(Atom, DisplayName)
%%   alias/2           alias(ClubAtom, AliasAtom)
%%   hours_per_week/2  hours_per_week(ClubAtom, Hours)
%%   performances_per_year/2
%%   competes/1        competes(ClubAtom)          — only asserted when true
%%   travels/1         travels(ClubAtom)
%%   performs_downtown/1
%%   collects_dues/1
%%   big_little/1
%%   performance_contract/1
%%   does_covers/1
%%   dance_style/2     dance_style(ClubAtom, StyleAtom)
%%   culture/2         culture(ClubAtom, CultureAtom)
%%   skill_level/2     skill_level(ClubAtom, Level)  — beginner/intermediate/advanced
%%   sister_club/2     sister_club(ClubA, ClubB)     — bidirectional
%%
%% Rules
%%   clubs_with_style/2, clubs_with_culture/2, beginner_friendly/1,
%%   low_commitment/2, high_performance/2, recommend/3

:- discontiguous club/2, alias/2, hours_per_week/2, performances_per_year/2.
:- discontiguous competes/1, travels/1, performs_downtown/1.
:- discontiguous collects_dues/1, big_little/1, performance_contract/1, does_covers/1.
:- discontiguous dance_style/2, culture/2, skill_level/2, sister_club/2.

%% Lion Dance Team (LDT)
club(lion_dance_team_ldt, 'Lion Dance Team (LDT)').
alias(lion_dance_team_ldt, ldt).
hours_per_week(lion_dance_team_ldt, 2).
performances_per_year(lion_dance_team_ldt, 10).
travels(lion_dance_team_ldt).
performs_downtown(lion_dance_team_ldt).
dance_style(lion_dance_team_ldt, lion_dance).
culture(lion_dance_team_ldt, chinese).
skill_level(lion_dance_team_ldt, beginner).
sister_club(lion_dance_team_ldt, cal_poly_csa).

%% Shan Wu Dance Team
club(shan_wu_dance_team, 'Shan Wu Dance Team').
hours_per_week(shan_wu_dance_team, 4).
performances_per_year(shan_wu_dance_team, 5).
performance_contract(shan_wu_dance_team).
does_covers(shan_wu_dance_team).
dance_style(shan_wu_dance_team, chinese_classical).
dance_style(shan_wu_dance_team, ballet_esque).
dance_style(shan_wu_dance_team, chinese_fusion).
culture(shan_wu_dance_team, chinese).
skill_level(shan_wu_dance_team, beginner).
skill_level(shan_wu_dance_team, intermediate).
skill_level(shan_wu_dance_team, advanced).
sister_club(shan_wu_dance_team, cal_poly_csa).

%% SLO Breakers
club(slo_breakers, 'SLO Breakers').
hours_per_week(slo_breakers, 4).
performances_per_year(slo_breakers, 5).
competes(slo_breakers).
travels(slo_breakers).
collects_dues(slo_breakers).
big_little(slo_breakers).
dance_style(slo_breakers, break_dancing).
dance_style(slo_breakers, freestyle).
skill_level(slo_breakers, beginner).
skill_level(slo_breakers, intermediate).
skill_level(slo_breakers, advanced).
sister_club(slo_breakers, k2).
sister_club(slo_breakers, united_movement).

%% Trăm Phần Trăm (TPT)
club(tram_phan_tram_tpt, 'Trăm Phần Trăm (TPT)').
alias(tram_phan_tram_tpt, tpt).
hours_per_week(tram_phan_tram_tpt, 2).
performances_per_year(tram_phan_tram_tpt, 3).
collects_dues(tram_phan_tram_tpt).
performance_contract(tram_phan_tram_tpt).
dance_style(tram_phan_tram_tpt, vietnamese_traditional).
dance_style(tram_phan_tram_tpt, modern).
culture(tram_phan_tram_tpt, vietnamese).
skill_level(tram_phan_tram_tpt, beginner).
skill_level(tram_phan_tram_tpt, intermediate).
skill_level(tram_phan_tram_tpt, advanced).
sister_club(tram_phan_tram_tpt, vietnamese_student_association).

%% PCE Kasayahan
club(pce_kasayahan, 'PCE Kasayahan').
hours_per_week(pce_kasayahan, 4).
performances_per_year(pce_kasayahan, 5).
collects_dues(pce_kasayahan).
does_covers(pce_kasayahan).
dance_style(pce_kasayahan, filipino_traditional).
culture(pce_kasayahan, filipino).
skill_level(pce_kasayahan, beginner).
skill_level(pce_kasayahan, intermediate).
skill_level(pce_kasayahan, advanced).
sister_club(pce_kasayahan, pce_modern).

%% PCE Modern
club(pce_modern, 'PCE Modern').
hours_per_week(pce_modern, 4).
performances_per_year(pce_modern, 4).
collects_dues(pce_modern).
big_little(pce_modern).
dance_style(pce_modern, open_style).
culture(pce_modern, filipino).
skill_level(pce_modern, beginner).
skill_level(pce_modern, intermediate).
skill_level(pce_modern, advanced).
sister_club(pce_modern, pce_kasayahan).

%% Kaja Krew
club(kaja_krew, 'Kaja Krew').
alias(kaja_krew, k2).
hours_per_week(kaja_krew, 4).
performances_per_year(kaja_krew, 5).
collects_dues(kaja_krew).
big_little(kaja_krew).
performance_contract(kaja_krew).
does_covers(kaja_krew).
dance_style(kaja_krew, k_pop).
dance_style(kaja_krew, open_style).
culture(kaja_krew, korean).
skill_level(kaja_krew, beginner).
skill_level(kaja_krew, intermediate).
skill_level(kaja_krew, advanced).
sister_club(kaja_krew, united_movement).
sister_club(kaja_krew, slo_breakers).

%% CPSalsa
club(cpsalsa, 'CPSalsa').
hours_per_week(cpsalsa, 4).
performances_per_year(cpsalsa, 9).
travels(cpsalsa).
collects_dues(cpsalsa).
dance_style(cpsalsa, salsa).
dance_style(cpsalsa, bachata).
skill_level(cpsalsa, beginner).
skill_level(cpsalsa, intermediate).
skill_level(cpsalsa, advanced).

%% Tahitian
club(tahitian, 'Tahitian').
hours_per_week(tahitian, 3).
performances_per_year(tahitian, 6).
dance_style(tahitian, tahitian_cultural_dance).
culture(tahitian, asian).
skill_level(tahitian, beginner).
skill_level(tahitian, intermediate).
skill_level(tahitian, advanced).

%% United Movement
club(united_movement, 'United Movement').
alias(united_movement, um).
hours_per_week(united_movement, 6).
performances_per_year(united_movement, 6).
competes(united_movement).
travels(united_movement).
collects_dues(united_movement).
big_little(united_movement).
performance_contract(united_movement).
dance_style(united_movement, hip_hop).
skill_level(united_movement, beginner).
skill_level(united_movement, intermediate).
skill_level(united_movement, advanced).
sister_club(united_movement, slo_breakers).
sister_club(united_movement, k2).

%% Merge
club(merge, 'Merge').
hours_per_week(merge, 3).
performances_per_year(merge, 1).
dance_style(merge, contemporary).
dance_style(merge, jazz).
skill_level(merge, beginner).
skill_level(merge, intermediate).
skill_level(merge, advanced).

%% Ballroom Team
club(ballroom_team, 'Ballroom Team').
performances_per_year(ballroom_team, 7).
competes(ballroom_team).
travels(ballroom_team).
collects_dues(ballroom_team).
performance_contract(ballroom_team).
dance_style(ballroom_team, ballroom).
skill_level(ballroom_team, beginner).
skill_level(ballroom_team, intermediate).
skill_level(ballroom_team, advanced).

%% Andaaz
club(andaaz, 'Andaaz').
hours_per_week(andaaz, 10).
performances_per_year(andaaz, 8).
competes(andaaz).
travels(andaaz).
performs_downtown(andaaz).
collects_dues(andaaz).
does_covers(andaaz).
dance_style(andaaz, fusion).
dance_style(andaaz, hip_hop).
dance_style(andaaz, contemporary).
dance_style(andaaz, bollywood).
dance_style(andaaz, bhangra).
dance_style(andaaz, classical_indian).
dance_style(andaaz, kuthu).
culture(andaaz, indian).
skill_level(andaaz, intermediate).
sister_club(andaaz, isa).

%% Imagen y Espiritu Ballet Folklorico
club(imagen_y_espiritu_ballet_folklorico, 'Imagen y Espiritu Ballet Folklorico').
hours_per_week(imagen_y_espiritu_ballet_folklorico, 4).
performances_per_year(imagen_y_espiritu_ballet_folklorico, 9).
collects_dues(imagen_y_espiritu_ballet_folklorico).
does_covers(imagen_y_espiritu_ballet_folklorico).
dance_style(imagen_y_espiritu_ballet_folklorico, ballet_folklorico).
culture(imagen_y_espiritu_ballet_folklorico, latino_chicano).
skill_level(imagen_y_espiritu_ballet_folklorico, beginner).
skill_level(imagen_y_espiritu_ballet_folklorico, intermediate).
skill_level(imagen_y_espiritu_ballet_folklorico, advanced).

%% Drag Club
club(drag_club, 'Drag Club').
hours_per_week(drag_club, 1).
performances_per_year(drag_club, 5).
performs_downtown(drag_club).
big_little(drag_club).
dance_style(drag_club, freestyle).
dance_style(drag_club, voguing).
dance_style(drag_club, waacking).
culture(drag_club, queer).
skill_level(drag_club, beginner).
skill_level(drag_club, intermediate).
skill_level(drag_club, advanced).

%% Look up a club by its display name (case-sensitive exact match).
%% ?- club_by_name('PCE Kasayahan', Club, DisplayName).
club_by_name(SearchName, Club, DisplayName) :-
    club(Club, DisplayName),
    DisplayName = SearchName.



%% Which clubs perform a given dance style?
%% ?- clubs_with_style(hip_hop, X).
clubs_with_style(Style, Club) :-
    dance_style(Club, Style).

%% Which clubs are associated with a given culture?
%% ?- clubs_with_culture(korean, X).
clubs_with_culture(Culture, Club) :-
    culture(Club, Culture).

%% Clubs that accept beginners.
beginner_friendly(Club) :-
    skill_level(Club, beginner).

%% Clubs with at most MaxHours practice hours per week.
%% ?- low_commitment(3, X).
low_commitment(MaxHours, Club) :-
    hours_per_week(Club, H),
    H =< MaxHours.

%% Clubs that perform at least MinPerfs times per year.
%% ?- high_performance(6, X).
high_performance(MinPerfs, Club) :-
    performances_per_year(Club, P),
    P >= MinPerfs.

%% General recommendation: style + skill level.
%% ?- recommend(hip_hop, beginner, X).
recommend(Style, Level, Club) :-
    dance_style(Club, Style),
    skill_level(Club, Level).

%% Clubs that do NOT collect dues.
free_to_join(Club) :-
    club(Club, _),
    \+ collects_dues(Club).

%% Clubs with a big/little mentorship program.
has_mentorship(Club) :-
    big_little(Club).

%% Clubs that compete AND travel.
competitive_travel(Club) :-
    competes(Club),
    travels(Club).
