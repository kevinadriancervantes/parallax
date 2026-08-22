function build_evidence_figures()
%BUILD_EVIDENCE_FIGURES Rebuild the public Parallax evidence figures.
%
% The script reads only the two accepted aggregate result artifacts copied
% into figures/data. It validates their repository-authority SHA-256 values,
% writes the plotted data, and renders the figures without model/provider
% calls or manual value entry.

script_dir = fileparts(mfilename('fullpath'));
figures_dir = fileparts(script_dir);
data_dir = fullfile(figures_dir, 'data');

dose_source = fullfile(data_dir, 'accepted-dose-profile.json');
nuisance_source = fullfile(data_dir, 'accepted-nuisance-profile.json');
dose_sha = '4511ad91028773c004697c8fdcf9d905f8265ebadd2b32c58945739cc35a8b01';
nuisance_sha = 'a5a7c422e4f69b86c663c0f0657ac46c552e5ff002a99aaa06cbc6f541e5df05';

assert(strcmp(sha256_file(dose_source), dose_sha), 'Accepted dose source identity mismatch.');
assert(strcmp(sha256_file(nuisance_source), nuisance_sha), 'Accepted nuisance source identity mismatch.');

dose = jsondecode(fileread(dose_source));
nuisance = jsondecode(fileread(nuisance_source));

scenario_ids = {'R01-FD-01', 'R01-FD-02', 'R01-FD-03'};
scenario_names = {'Cedar Ridge', 'Morrow Basin', 'Lumen'};
dose_ids = {'STRONG_AGAINST', 'WEAK_AGAINST', 'BASELINE', 'WEAK_TOWARD', 'STRONG_TOWARD'};
dose_labels = {'Strong -', 'Weak -', 'Baseline', 'Weak +', 'Strong +'};
capacities = {'7B', '7B', '14B', '14B'};
regimes = {'D', 'S', 'D', 'S'};
strata = {'7B-D', '7B-S', '14B-D', '14B-S'};

%% Figure A data: all-scheduled response-state shares.
n = numel(scenario_ids) * numel(strata) * numel(dose_ids);
scenario_id = strings(n,1); scenario_name = strings(n,1); stratum = strings(n,1);
capacity = strings(n,1); regime = strings(n,1); dose_id = strings(n,1);
dose_index = zeros(n,1); scheduled = zeros(n,1);
leans_not_h_rate = zeros(n,1); unresolved_rate = zeros(n,1);
leans_h_rate = zeros(n,1); unusable_rate = zeros(n,1);

k = 0;
for s = 1:numel(scenario_ids)
    for q = 1:numel(strata)
        profile = find_profile(dose.profiles, scenario_ids{s}, capacities{q}, regimes{q});
        for d = 1:numel(dose_ids)
            k = k + 1;
            state = profile.doses.(dose_ids{d});
            scenario_id(k) = scenario_ids{s};
            scenario_name(k) = scenario_names{s};
            stratum(k) = strata{q};
            capacity(k) = capacities{q};
            regime(k) = regimes{q};
            dose_id(k) = dose_ids{d};
            dose_index(k) = d;
            scheduled(k) = state.scheduled;
            leans_not_h_rate(k) = state.state_all_scheduled.LEANS_NOT_H.rate;
            unresolved_rate(k) = state.state_all_scheduled.UNRESOLVED.rate;
            leans_h_rate(k) = state.state_all_scheduled.LEANS_H.rate;
            unusable_rate(k) = state.local_unusable.rate;
            total = leans_not_h_rate(k) + unresolved_rate(k) + leans_h_rate(k) + unusable_rate(k);
            assert(abs(total - 1) < 1e-12, 'Response shares do not sum to one.');
        end
    end
end

profile_table = table(scenario_id, scenario_name, stratum, capacity, regime, dose_id, ...
    dose_index, scheduled, leans_not_h_rate, unresolved_rate, leans_h_rate, unusable_rate);
writetable(profile_table, fullfile(data_dir, 'local-model-evidence-response-profile.csv'));

colors = [0.77 0.31 0.19; 0.72 0.74 0.76; 0.10 0.42 0.55; 0.19 0.16 0.24];
fig_a = figure('Visible','off','Color','white','Units','pixels','Position',[100 100 1740 1420], ...
    'PaperPositionMode','auto','Renderer','painters');
layout = tiledlayout(fig_a, 4, 3, 'TileSpacing','compact', 'Padding','compact');

for q = 1:numel(strata)
    for s = 1:numel(scenario_ids)
        ax = nexttile(layout, (q-1)*3+s);
        mask = profile_table.scenario_id == scenario_ids{s} & profile_table.stratum == strata{q};
        rows = profile_table(mask,:);
        [~, order] = sort(rows.dose_index);
        rows = rows(order,:);
        values = [rows.leans_not_h_rate, rows.unresolved_rate, rows.leans_h_rate, rows.unusable_rate];
        bars = bar(ax, 1:5, values, 'stacked', 'BarWidth', 0.82, 'EdgeColor',[1 1 1], 'LineWidth',0.5);
        for c = 1:4
            bars(c).FaceColor = colors(c,:);
        end
        hold(ax,'on');
        cumulative = zeros(5,1);
        symbols = {'N','U','H','X'};
        for c = 1:4
            for x = 1:5
                v = values(x,c);
                if v >= 0.12
                    if c == 2
                        tc = [0.08 0.10 0.12];
                    else
                        tc = [1 1 1];
                    end
                    text(ax, x, cumulative(x)+v/2, sprintf('%s %.0f', symbols{c}, 100*v), ...
                        'HorizontalAlignment','center','VerticalAlignment','middle', ...
                        'FontName','Arial','FontSize',7,'FontWeight','bold','Color',tc);
                end
                cumulative(x) = cumulative(x) + v;
            end
        end
        hold(ax,'off');
        ylim(ax,[0 1]); xlim(ax,[0.45 5.55]);
        xticks(ax,1:5); xticklabels(ax,dose_labels); xtickangle(ax,28);
        yticks(ax,0:0.25:1); yticklabels(ax,{'0','25%','50%','75%','100%'});
        grid(ax,'on'); ax.YGrid = 'on'; ax.XGrid = 'off'; ax.GridAlpha = 0.18;
        ax.FontName = 'Arial'; ax.FontSize = 8; ax.Box = 'off';
        title(ax, sprintf('%s | %s', strata{q}, scenario_names{s}), 'FontName','Arial', ...
            'FontSize',10,'FontWeight','bold');
        if s == 1
            ylabel(ax,'Share of scheduled outputs','FontName','Arial','FontSize',9);
        end
    end
end

title(layout, 'Local Qwen2.5 response states across ordered evidence', ...
    'FontName','Arial','FontSize',18,'FontWeight','bold');
xlabel(layout, 'Evidence dose (against H to toward H)', 'FontName','Arial','FontSize',11);
legend(bars, {'N = LEANS NOT H','U = UNRESOLVED','H = LEANS H','X = unusable'}, ...
    'Orientation','horizontal','Location','southoutside','FontName','Arial','FontSize',9);

exportgraphics(fig_a, fullfile(figures_dir, 'local-model-evidence-response-profile.svg'), ...
    'ContentType','vector','BackgroundColor','white');
export_png_deterministic(fig_a, fullfile(figures_dir, 'local-model-evidence-response-profile.png'), ...
    160, [1 1 1]);
close(fig_a);

%% Figure B data: maximum absolute A-B difference across primary shares.
n2 = numel(scenario_ids) * numel(dose_ids) * numel(strata);
scenario_id = strings(n2,1); scenario_name = strings(n2,1); dose_id = strings(n2,1);
dose_index = zeros(n2,1); stratum = strings(n2,1); capacity = strings(n2,1); regime = strings(n2,1);
diff_leans_not_h = zeros(n2,1); diff_unresolved = zeros(n2,1);
diff_leans_h = zeros(n2,1); diff_unusable = zeros(n2,1);
max_abs_primary_difference = zeros(n2,1); nonzero = false(n2,1);

k = 0;
for s = 1:numel(scenario_ids)
    for d = 1:numel(dose_ids)
        for q = 1:numel(strata)
            k = k + 1;
            comp = find_comparison(nuisance.comparisons, scenario_ids{s}, dose_ids{d}, capacities{q}, regimes{q});
            scenario_id(k) = scenario_ids{s}; scenario_name(k) = scenario_names{s};
            dose_id(k) = dose_ids{d}; dose_index(k) = d; stratum(k) = strata{q};
            capacity(k) = capacities{q}; regime(k) = regimes{q};
            diff_leans_not_h(k) = comp.differences.state_LEANS_NOT_H_all_scheduled;
            diff_unresolved(k) = comp.differences.state_UNRESOLVED_all_scheduled;
            diff_leans_h(k) = comp.differences.state_LEANS_H_all_scheduled;
            diff_unusable(k) = comp.differences.local_unusable_rate;
            values = [diff_leans_not_h(k), diff_unresolved(k), diff_leans_h(k), diff_unusable(k)];
            max_abs_primary_difference(k) = max(abs(values));
            nonzero(k) = max_abs_primary_difference(k) > 1e-12;
        end
    end
end
assert(sum(nonzero) == 17, 'Accepted nuisance nonzero-comparison count changed.');

nuisance_table = table(scenario_id, scenario_name, dose_id, dose_index, stratum, capacity, regime, ...
    diff_leans_not_h, diff_unresolved, diff_leans_h, diff_unusable, ...
    max_abs_primary_difference, nonzero);
writetable(nuisance_table, fullfile(data_dir, 'nuisance-instability-matrix.csv'));

matrix = zeros(15,4);
row_labels = strings(15,1);
for s = 1:3
    for d = 1:5
        row = (s-1)*5+d;
        row_labels(row) = sprintf('%s | %s', scenario_names{s}, dose_labels{d});
        for q = 1:4
            mask = nuisance_table.scenario_id == scenario_ids{s} & ...
                nuisance_table.dose_id == dose_ids{d} & nuisance_table.stratum == strata{q};
            matrix(row,q) = nuisance_table.max_abs_primary_difference(mask);
        end
    end
end

fig_b = figure('Visible','off','Color','white','Units','pixels','Position',[100 100 1160 1120], ...
    'PaperPositionMode','auto','Renderer','painters');
ax = axes(fig_b,'Position',[0.29 0.10 0.60 0.78]);
imagesc(ax,matrix,[0 1]);
base = [1 1 1]; peak = [0.47 0.12 0.33];
t = linspace(0,1,256)';
colormap(ax, base.*(1-t) + peak.*t);
colorbar(ax,'eastoutside','Ticks',[0 .25 .5 .75 1], ...
    'TickLabels',{'0','25','50','75','100 pp'});
xticks(ax,1:4); xticklabels(ax,strata);
yticks(ax,1:15); yticklabels(ax,row_labels);
ax.FontName='Arial'; ax.FontSize=9; ax.TickLength=[0 0]; ax.Box='on';
xlabel(ax,'Local-model stratum','FontName','Arial','FontSize',11);
ylabel(ax,'Blinded scenario / evidence-dose pair','FontName','Arial','FontSize',11);
hold(ax,'on');
for y = 1:15
    for x = 1:4
        value = matrix(y,x);
        if value < 1e-12
            label = '-';
            tc = [0.25 0.27 0.30];
        else
            label = sprintf('%.0f',100*value);
            if value > 0.46; tc = [1 1 1]; else; tc = [0.14 0.08 0.12]; end
        end
        text(ax,x,y,label,'HorizontalAlignment','center','VerticalAlignment','middle', ...
            'FontName','Arial','FontSize',9,'FontWeight','bold','Color',tc);
    end
end
for boundary = [5.5 10.5]
    plot(ax,[0.5 4.5],[boundary boundary],'-','Color',[0.12 0.14 0.17],'LineWidth',2);
end
hold(ax,'off');
title(ax, {'Blinded A/B nuisance instability in the local Qwen exercise', ...
    'Cell = largest absolute A-B shift across four scheduled-denominator', ...
    'response-state shares (percentage points)'}, ...
    'FontName','Arial','FontSize',12,'FontWeight','bold');

exportgraphics(fig_b, fullfile(figures_dir, 'nuisance-instability-matrix.svg'), ...
    'ContentType','vector','BackgroundColor','white');
export_png_deterministic(fig_b, fullfile(figures_dir, 'nuisance-instability-matrix.png'), ...
    170, [1 1 1]);
close(fig_b);

%% Social card (editorial metadata only; no quantitative inference).
fig_c = figure('Visible','off','Color',[0.965 0.949 0.910],'Units','pixels', ...
    'Position',[100 100 1200 630],'PaperPositionMode','auto','Renderer','painters');
ax = axes(fig_c,'Position',[0 0 1 1]); axis(ax,[0 1200 0 630]); axis(ax,'off'); hold(ax,'on');
rectangle(ax,'Position',[0 0 1200 630],'FaceColor',[0.965 0.949 0.910],'EdgeColor','none');
rectangle(ax,'Position',[0 0 35 630],'FaceColor',[0.08 0.22 0.30],'EdgeColor','none');
text(ax,92,535,'PARALLAX','FontName','Arial','FontSize',22,'FontWeight','bold','Color',[0.63 0.25 0.13]);
text(ax,92,420,{'How do we test strategic AI advice','when there is no answer key?'}, ...
    'FontName','Arial','FontSize',38,'FontWeight','bold','Color',[0.08 0.12 0.16], ...
    'VerticalAlignment','middle');
text(ax,92,236,{'Experiment 1 failed its frozen rule. The instrument was rebuilt.', ...
    'The evidence trail - including real local Qwen behavior - is public.'}, ...
    'FontName','Arial','FontSize',18,'Color',[0.25 0.29 0.31],'VerticalAlignment','middle');
rectangle(ax,'Position',[92 72 520 62],'Curvature',0.08,'FaceColor',[0.08 0.22 0.30],'EdgeColor','none');
text(ax,115,103,'parallax.midex.app','FontName','Arial','FontSize',18,'FontWeight','bold', ...
    'Color',[1 1 1],'VerticalAlignment','middle');
text(ax,1100,103,'ChinaTalk 2026','FontName','Arial','FontSize',15,'FontWeight','bold', ...
    'Color',[0.36 0.18 0.13],'HorizontalAlignment','right','VerticalAlignment','middle');
hold(ax,'off');
export_png_deterministic(fig_c, fullfile(figures_dir, 'social-preview.png'), ...
    100, [0.965 0.949 0.910]);
close(fig_c);

fid = fopen(fullfile(data_dir, 'matlab-runtime.txt'),'w','n','UTF-8');
assert(fid >= 0, 'Unable to write MATLAB runtime receipt.');
fprintf(fid, 'MATLAB %s\n', version);
fclose(fid);

fprintf('PARALLAX_EVIDENCE_FIGURES_BUILT\n');
fprintf('profile_rows=%d\n', height(profile_table));
fprintf('nuisance_rows=%d\n', height(nuisance_table));
fprintf('nuisance_nonzero=%d\n', sum(nonzero));
end

function profile = find_profile(profiles, scenario_id, capacity, regime)
for i = 1:numel(profiles)
    candidate = profiles(i);
    if strcmp(candidate.scenario_id, scenario_id) && strcmp(candidate.capacity, capacity) && strcmp(candidate.regime, regime)
        profile = candidate;
        return;
    end
end
error('Profile not found: %s/%s/%s', scenario_id, capacity, regime);
end

function comparison = find_comparison(comparisons, scenario_id, dose_id, capacity, regime)
for i = 1:numel(comparisons)
    candidate = comparisons(i);
    if strcmp(candidate.scenario_id, scenario_id) && strcmp(candidate.dose, dose_id) && ...
            strcmp(candidate.capacity, capacity) && strcmp(candidate.regime, regime)
        comparison = candidate;
        return;
    end
end
error('Comparison not found: %s/%s/%s/%s', scenario_id, dose_id, capacity, regime);
end

function digest = sha256_file(path)
fid = fopen(path,'rb');
assert(fid >= 0, 'Unable to open file for hashing: %s', path);
bytes = fread(fid, Inf, '*uint8');
fclose(fid);
md = java.security.MessageDigest.getInstance('SHA-256');
md.update(bytes);
raw = typecast(md.digest(),'uint8');
digest = lower(reshape(dec2hex(raw,2).',1,[]));
end

function export_png_deterministic(fig, path, resolution, background)
% exportgraphics may emit changing ancillary PNG metadata. Re-encoding only
% its rendered pixels with imwrite produces byte-stable public artifacts.
temporary = [path '.render.png'];
exportgraphics(fig, temporary, 'Resolution',resolution,'BackgroundColor',background);
pixels = imread(temporary);
imwrite(pixels, path, 'png');
delete(temporary);
end
