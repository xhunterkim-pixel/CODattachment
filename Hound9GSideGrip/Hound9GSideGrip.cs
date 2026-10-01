using System.Reflection;
using SPTarkov.DI.Annotations;
using SPTarkov.Server.Core.DI;
using SPTarkov.Server.Core.Models.Spt.Mod;
using Range = SemanticVersioning.Range;
using Version = SemanticVersioning.Version;

namespace Hound9GSideGrip;

public record ModMetadata : IModMetadata
{
    public string ModGuid { get; init; } = "com.hound.hound9gsidegrip";
    public string Name { get; init; } = "Hound9GSideGrip";
    public string Author { get; init; } = "Hound";
    public List<string>? Contributors { get; init; }
    public Version Version { get; init; } = new("1.0.0");
    public Range SptVersion { get; init; } = new("~4.1.3");
    public List<string>? Incompatibilities { get; init; }
    public Dictionary<string, Range>? ModDependencies { get; init; } = new()
    {
        { "com.wtt.commonlib", new Range("~3.0.6") }
    };
    public string? Url { get; init; }
    public string License { get; init; } = "MIT";
    public bool HasPrepatcher { get; init; } = false;
}

// Runs after the database has loaded, and after WTT-CommonLib is ready.
[Injectable(TypePriority = OnLoadOrder.Preload + 2)]
public class Hound9GSideGrip(WTTServerCommonLib.WTTServerCommonLib wttCommon) : IOnLoad
{
    public async Task OnLoadAsync(CancellationToken cancellationToken)
    {
        // Reads every item JSON in this mod's db/CustomItems folder.
        var assembly = Assembly.GetExecutingAssembly();
        await wttCommon.CustomItemServiceExtended.CreateCustomItems(assembly, Path.Join("db", "CustomItems"));
    }
}
