import { describe, it, expect } from 'vitest';
import { themes, defaultTheme, type Theme } from './themes';

describe('themes', () => {
  it('should have at least one theme', () => {
    expect(themes.length).toBeGreaterThan(0);
  });

  it('should have unique theme IDs', () => {
    const ids = themes.map(t => t.id);
    const uniqueIds = new Set(ids);
    expect(uniqueIds.size).toBe(ids.length);
  });

  it('each theme should have required properties', () => {
    themes.forEach((theme: Theme) => {
      expect(theme).toHaveProperty('name');
      expect(theme).toHaveProperty('id');
      expect(theme).toHaveProperty('colors');
    });
  });

  it('each theme should have non-empty name and id', () => {
    themes.forEach((theme: Theme) => {
      expect(theme.name.length).toBeGreaterThan(0);
      expect(theme.id.length).toBeGreaterThan(0);
    });
  });

  it('each theme should have all required color properties', () => {
    themes.forEach((theme: Theme) => {
      expect(theme.colors).toHaveProperty('primary');
      expect(theme.colors).toHaveProperty('primaryGlow');
      expect(theme.colors).toHaveProperty('bg');
      expect(theme.colors).toHaveProperty('bgSecondary');
      expect(theme.colors).toHaveProperty('border');
      expect(theme.colors).toHaveProperty('inputPlaceholder');
    });
  });

  it('each color should be a valid hex string', () => {
    const hexColorRegex = /^#[0-9A-Fa-f]{6}$/;
    themes.forEach((theme: Theme) => {
      Object.values(theme.colors).forEach(color => {
        expect(color).toMatch(hexColorRegex);
      });
    });
  });

  describe('specific themes', () => {
    it('should have Classic Green theme', () => {
      const greenTheme = themes.find(t => t.id === 'green');
      expect(greenTheme).toBeDefined();
      expect(greenTheme!.name).toBe('Classic Green');
      expect(greenTheme!.colors.primary).toBe('#33ff33');
    });

    it('should have Amber CRT theme', () => {
      const amberTheme = themes.find(t => t.id === 'amber');
      expect(amberTheme).toBeDefined();
      expect(amberTheme!.name).toBe('Amber CRT');
      expect(amberTheme!.colors.primary).toBe('#ffb000');
    });

    it('should have Blue Terminal theme', () => {
      const blueTheme = themes.find(t => t.id === 'blue');
      expect(blueTheme).toBeDefined();
      expect(blueTheme!.name).toBe('Blue Terminal');
      expect(blueTheme!.colors.primary).toBe('#00ffff');
    });

    it('should have Tokyo Cyberpunk theme', () => {
      const pinkTheme = themes.find(t => t.id === 'pink');
      expect(pinkTheme).toBeDefined();
      expect(pinkTheme!.name).toBe('Tokyo Cyberpunk');
    });

    it('should have Monochrome theme', () => {
      const monoTheme = themes.find(t => t.id === 'mono');
      expect(monoTheme).toBeDefined();
      expect(monoTheme!.name).toBe('Monochrome');
      expect(monoTheme!.colors.primary).toBe('#ffffff');
      expect(monoTheme!.colors.bg).toBe('#000000');
    });

    it('should have Simple theme', () => {
      const simpleTheme = themes.find(t => t.id === 'simple');
      expect(simpleTheme).toBeDefined();
      expect(simpleTheme!.name).toBe('Simple');
    });

    it('should have Blue-ish theme', () => {
      const blueishTheme = themes.find(t => t.id === 'blueish');
      expect(blueishTheme).toBeDefined();
      expect(blueishTheme!.name).toBe('Blue-ish');
    });
  });
});

describe('defaultTheme', () => {
  it('should be defined', () => {
    expect(defaultTheme).toBeDefined();
  });

  it('should match the first theme in themes array', () => {
    expect(defaultTheme).toEqual(themes[0]);
  });

  it('should have id of green', () => {
    expect(defaultTheme.id).toBe('green');
  });

  it('should have name of Classic Green', () => {
    expect(defaultTheme.name).toBe('Classic Green');
  });
});
