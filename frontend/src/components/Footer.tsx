import { useState, useEffect } from "react";
import { Flex, Link } from "@chakra-ui/react";

const Footer = () => {
  const [timestamp, setTimestamp] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => {
      setTimestamp(new Date());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  return (
    <Flex
      as="footer"
      align="center"
      justify="space-between"
      wrap="wrap"
      padding="0.75rem 1rem"
      bg="var(--theme-bg-secondary)"
      borderTop="2px solid var(--theme-border)"
      width="100%"
      position="fixed"
      bottom="0"
      left="0"
      right="0"
      zIndex="1000"
      boxShadow="0 0 10px var(--theme-primary)"
      fontFamily="'VT323', 'Courier New', Courier, monospace"
    >
      <Flex align="center" gap={4}>
        <Link
          href="https://github.com/tomnis/coldbrewer"
          isExternal
          className="terminal-glow"
          style={{ fontSize: "0.9em", textDecoration: "none" }}
          _hover={{ color: "var(--theme-primary)" }}
        >
          [GitHub]
        </Link>
      </Flex>
      <Flex align="center" gap={4}>
        <span className="terminal-glow" style={{ fontSize: "0.9em" }}>
          [System Ready]
        </span>
        <span className="terminal-glow" style={{ fontSize: "0.9em" }}>
          {formatTime(timestamp)}
        </span>
      </Flex>
    </Flex>
  );
};

export default Footer;
